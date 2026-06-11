import argparse
import logging
import signal
import subprocess
import sys
import time
from subprocess import CalledProcessError

import boto3.session
from pygit2 import Repository

AWS_REGION = "us-east-1"  # TODO: FILL ME IN
AWS_PROFILE_NAME = "sample-django-app"  # TODO: FILL ME IN


MIGRATION_TIMEOUT_SECONDS = 10 * 60  # Ten minutes
STATUS_CHECK_INTERVAL = 5
STATUS_REPORT_FREQUENCY = 6 # Report every 6 checks


class MigrationFailed(Exception):
    pass


class MigrationTimeOut(Exception):
    pass


class SetupFailed(Exception):
    pass

#######################
# Deploy steps
#######################

def deploy(args):
    if not args.no_input:
        # Request user confirmation
        confirmation_message = f"\nBegin deploying to {args.env}? "
        if args.use_image_from_env:
            confirmation_message += f"This will use the current {args.use_image_from_env} deployment. "
        elif args.use_latest:
            confirmation_message += "This will use the imaged tagged 'latest'. "
        elif args.skip_build:
            confirmation_message += "This will reuse the currently deployed code. "
        else:
            confirmation_message += f"This will build using the current branch ({Repository('.').head.shorthand}). "
        confirmation_message += "(y/n): "
        confirmation = input(confirmation_message)
        if confirmation.lower() not in ["y", "yes"]:
            logging.warning("Deployment canceled.")
            return

    # Local state setup for relevant envs
    terraform_envs = [args.env]
    if args.use_image_from_env:
        terraform_envs.append(args.use_image_from_env)
    try:
        setup(terraform_envs)
    except SetupFailed:
        # Setup prints error info
        raise SystemExit()

    # ECR image setup
    if args.use_image_from_env:
        copy_image_from_env(args.use_image_from_env, args.env, args.profile)
    elif args.use_latest:
        copy_latest_image(args.env)
    elif not args.skip_build:
        build_and_push_image(args.env, args.profile, args.use_remote_cache)
    else:
        logging.info("Skipping build step")

    if args.skip_migration:
        logging.info("Skipping database migration")
    else:
        # START_FEATURE celery
        # Stop worker server prior to running migrations
        stop_worker_service(args.env)
        # END_FEATURE celery
        # Run and wait for migrations
        run_migrations(args.env)

    # Redeploy services
    restart_services(args.env)


def build_and_push_image(env, profile, use_remote_cache):
    # Authenticate for ECR
    ecr_repository_name = get_terraform_output("ecr_repository_name", env)
    ecr_image_uri = get_terraform_output("ecr_image_uri", env)
    ecr_login(ecr_image_uri, profile)

    # Build and push image
    logging.info("Building docker image and pushing to ECR...")
    build_command = [
        "docker", "buildx", "build", "--platform=linux/amd64", "--push", "-t", ecr_image_uri, ".",
    ]
    if use_remote_cache:
        build_command.extend([
            #"--builder=container",
            "--cache-to",
            f"type=inline",
            "--cache-from",
            f"type=registry,ref={ecr_image_uri}"
        ])
    subprocess.run(build_command, check=True)

    # Remove unused docker images to preserve local disk space
    subprocess.run(["docker", "image", "prune", "-f"])


def copy_image_from_env(from_env, to_env, profile):
    # Retags image from from_env into to_env.
    logging.info(f"Copying image from {from_env} to {to_env}")
    from_ecr_repository_name = get_terraform_output("ecr_repository_name", from_env)
    to_ecr_repository_name = get_terraform_output("ecr_repository_name", to_env)

    if from_ecr_repository_name == to_ecr_repository_name:
        retag_image(from_ecr_repository_name, from_env, to_env)
    else:
        # Pull image
        from_image_uri = get_terraform_output("ecr_image_uri", from_env)
        subprocess.run(["docker", "pull", from_image_uri], check=True)

        # Push image
        to_image_uri = get_terraform_output("ecr_image_uri", to_env)
        subprocess.run(["docker", "tag", from_image_uri, to_image_uri], check=True)
        subprocess.run(["docker", "push", to_image_uri], check=True)
        # Remove unused docker images to preserve local disk space
        subprocess.run(["docker", "image", "prune", "-f"])


def copy_latest_image(env):
    # Retags latest image in repository for use by env
    logging.info(f"Copying latest image to {env}")
    ecr_repository_name = get_terraform_output("ecr_repository_name", env)
    retag_image(ecr_repository_name, "latest", env)


def retag_image(repository, from_tag, to_tag):
    ecr_client = boto3.client("ecr")
    # Get image manifest
    image_response = ecr_client.batch_get_image(
        repositoryName=repository,
        imageIds=[{
            "imageTag": from_tag
        }],
        acceptedMediaTypes=["string"]
    )
    image_manifest = image_response["images"][0]["imageManifest"]
    image_manifest_media_type = image_response["images"][0]["imageManifestMediaType"]
    # Add new tag to manifest
    ecr_client.put_image(
        repositoryName=repository,
        imageManifest=image_manifest,
        imageTag=to_tag,
        imageManifestMediaType=image_manifest_media_type,
    )


def run_migrations(env):
    # Runs a migration task using the web server task definition with an overridden command
    cluster_id = get_terraform_output("cluster_id", env)
    ecs_client = boto3.client("ecs")
    logging.info("Starting migrations...")
    run_task_response = ecs_client.run_task(
        taskDefinition=get_terraform_output("web_task_definition_arn", env),
        networkConfiguration={
            "awsvpcConfiguration" : {
                "subnets": [get_terraform_output("web_network_configuration_subnet", env)],
                "securityGroups": [get_terraform_output("web_network_configuration_security_group", env)],
                "assignPublicIp": "ENABLED"
            }
        },
        cluster=cluster_id,
        capacityProviderStrategy=[{'capacityProvider': 'FARGATE'}],
        overrides={
            "containerOverrides": [{
                "name": get_terraform_output("web_service_name", env),
                "command": ["python", "manage.py", "migrate", "--no-input"]
            }]
        }
    )

    # Wait for task to complete. Times out after MIGRATION_TIMEOUT_SECONDS
    migration_task_id = run_task_response["tasks"][0]["taskArn"]
    logging.info(f"Migration task provisioned with ID {migration_task_id}")
    start = time.time()
    wait_index = 0

    while time.time() - start < MIGRATION_TIMEOUT_SECONDS:
        if wait_index % STATUS_REPORT_FREQUENCY == 0:
            logging.info("Waiting for migrations to finish...")
        wait_index += 1
        describe_tasks_response = ecs_client.describe_tasks(cluster=cluster_id, tasks=[migration_task_id])
        task = describe_tasks_response["tasks"][0]
        stop_code = task.get("stopCode")
        if not stop_code:
            time.sleep(STATUS_CHECK_INTERVAL)
            continue
        if stop_code == "EssentialContainerExited":
            # The migration task has finished
            container = task["containers"][0]
            exit_code = container.get("exitCode")
            if exit_code == 0:
                logging.info("Migration complete")
                return
            error_message = f"exit code {exit_code} and reason {container.get('reason')}"
        else:
            error_message = f"code {stop_code} and reason {task.get('stoppedReason')}"
        logging.error(
            f"Migration task failed with {error_message}."
            f"Check log stream for more info: {cloudwatch_log_url(env)}"
        )
        raise MigrationFailed()
    logging.error(
        f"Migration timed out. It may still be running. Check log stream for more info: {cloudwatch_log_url(env)}"
    )
    raise MigrationTimeOut()
# START_FEATURE celery
def stop_worker_service(env):
    logging.info("Stopping worker service")
    cluster_id = get_terraform_output("cluster_id", env)
    service_name = get_terraform_output("worker_service_name", env)
    ecs_client = boto3.client("ecs")
    ecs_client.update_service(
        cluster=cluster_id,
        service=service_name,
        desiredCount=0
    )
    # Desired status may not have updated immediately -- try both RUNNING and STOPPED
    task_arns = ecs_client.list_tasks(cluster=cluster_id, serviceName=service_name)["taskArns"]
    if not task_arns:
        task_arns = ecs_client.list_tasks(
            cluster=cluster_id, serviceName=service_name, desiredStatus="STOPPED"
        )["taskArns"]
    if not task_arns:
        logging.info("No worker tasks to stop")
        return
    wait_index = 0
    while True:
        tasks = ecs_client.describe_tasks(cluster=cluster_id, tasks=task_arns)["tasks"]
        if all(task.get("stoppedAt") for task in tasks):
            break
        if wait_index % STATUS_REPORT_FREQUENCY == 0:
            logging.info("Waiting for worker service to stop...")
        wait_index += 1
        time.sleep(STATUS_CHECK_INTERVAL)
    logging.info("Worker service stopped")
# END_FEATURE celery


def restart_services(env):
    # START_FEATURE celery
    # Restarts both web and worker in parallel (order doesn't matter since communication is handled via redis)
    # END_FEATURE celery
    # Restart ECS web service to deploy new code
    logging.info("Redeploying web service...")
    web_service_name = get_terraform_output("web_service_name", env)
    cluster_id = get_terraform_output("cluster_id", env)
    ecs_client = boto3.client("ecs")
    ecs_client.update_service(
        cluster=cluster_id,
        service=web_service_name,
        forceNewDeployment=True,
    )
    service_names_to_check = [web_service_name]
    failed_task_ids = {}
    worker_service_name = None
    #START_FEATURE celery
    # Restart worker service to deploy new code and set the desired task count back to expected state
    logging.info("Redeploying worker service...")
    worker_service_name = get_terraform_output("worker_service_name", env)
    desired_task_count = get_terraform_output("worker_task_desired_count", env)
    ecs_client.update_service(
        cluster=cluster_id,
        service=worker_service_name,
        forceNewDeployment=True,
        desiredCount=int(desired_task_count)
    )
    service_names_to_check.append(worker_service_name)
    #END_FEATURE celery
    # Wait up to 30 min for deployment to complete
    for i in range(30 * int(60 / STATUS_CHECK_INTERVAL)):
        if i % STATUS_REPORT_FREQUENCY == 0:
            logging.info("Waiting for deployment to finish...")
        services_response = ecs_client.describe_services(
            cluster=cluster_id, services=service_names_to_check
        )
        in_progress_service_names = []

        for service in services_response["services"]:
            new_deployment = next(
                deployment for deployment in service["deployments"] if deployment["status"] == "PRIMARY"
            )
            deployment_state = new_deployment["rolloutState"]
            service_name = service['serviceName']
            is_worker = service_name == worker_service_name
            if new_deployment["failedTasks"] > 0 and not failed_task_ids.get(service_name):
                failed_task_ids[service_name] = new_deployment['id']
                logging.warning(f"Deployment task for {service_name} failed. Retrying...")
            if deployment_state == "IN_PROGRESS":
                in_progress_service_names.append(service_name)
            elif deployment_state == "COMPLETED":
                failed_id = failed_task_ids.get(service_name)
                if failed_id and failed_id != new_deployment['id']:
                    # original deployment did not succeed; rollback was successful
                    logging.error(
                        f"Deployment failed for {service_name}! Rolled back to last successful deployment. "
                        f"Check log stream for more info: {cloudwatch_log_url(env, worker=is_worker)}"
                    )
                    raise Exception("Deployment rolled back")
                else:
                    logging.info(f"Success! Deployment complete for service {service_name}.")
            elif deployment_state == "FAILED":
                logging.error(
                    f"Deployment failed for {service_name}! Reason: {new_deployment['rolloutStateReason']}. "
                    f"Check log stream for more info: {cloudwatch_log_url(env, worker=is_worker)}"
                )
            else:
                logging.warning(f"Unknown deployment state {deployment_state}. Please check the ECS console.")
        if in_progress_service_names:
            time.sleep(STATUS_CHECK_INTERVAL)
            service_names_to_check = in_progress_service_names
        else:
            return
    raise Exception("Too many retries. Please check the ECS console.")


#######################
# SSH
#######################

def ssh(args):
    # Runs a bash shell in a running task for the env. Note this may run in a short-lived task (e.g. migration task)
    # Refresh terraform state
    try:
        setup([args.env])
    except SetupFailed:
        return
    cluster_id = get_terraform_output("cluster_id", args.env)
    # START_FEATURE celery
    service_name_key = "web_service_name" if args.web else "worker_service_name"
    # END_FEATURE celery
    
    service_name = get_terraform_output(service_name_key, args.env)
    ecs_client = boto3.client("ecs")
    list_tasks_resp = ecs_client.list_tasks(cluster=cluster_id, serviceName=service_name)
    task_ids = list_tasks_resp["taskArns"]

    if task_ids:
        task_id = task_ids[0]
        bash_command = ["aws", "ecs", "execute-command", "--cluster", cluster_id, "--task", task_id,
                        "--region", AWS_REGION, "--profile", args.profile, "--interactive",
                        "--command", "'/bin/bash'"]
        with subprocess.Popen(bash_command) as cmd:
            ret = None
            while ret is None:
                try:
                    ret = cmd.wait()
                except KeyboardInterrupt:
                    cmd.send_signal(signal.SIGINT)
    else:
        print(f"No task id(s) found. Is the {service_name} server running?")
        if not args.web:
            print("Try running with --web")



##########################
# Helpers
##########################

def setup(envs):
    # Refresh terraform state
    logging.info("Refreshing terraform state...")
    for env in envs:
        try:
            subprocess.run(["terraform", "refresh"], cwd=f"terraform/envs/{env}", check=True, capture_output=True)
        except CalledProcessError as e:
            print(e.stderr.decode())
            logging.error(
                f"Terraform refresh failed -- see output above. \n"
                f"* Have you run terraform init in the terraform/envs/{env} directory? \n"
                f"* Are you authenticated with AWS?\n"
            )
            raise SetupFailed()


def subprocess_output(command_args, **subprocess_kwargs):
    try:
        output = subprocess.run(command_args, **subprocess_kwargs, capture_output=True, check=True)
        output = output.stdout.decode('utf-8').strip("\n").strip('"')
        # If the output contains newlines after stripping, we may be running a github action
        if "\n" in output:
            output = output.split("\n")[1].strip('"')
        return output
    except CalledProcessError as e:
        logging.error(e.stderr.decode())
        raise


def get_terraform_output(output_key, env):
    return subprocess_output(["terraform", "output", output_key], cwd=f"terraform/envs/{env}")


def ecr_login(ecr_image_uri, profile):
    logging.info("Logging in to ECR...")
    password_command = ["aws", "ecr", "get-login-password", "--region", AWS_REGION, "--profile", profile]
    password = subprocess_output(password_command)
    docker_login_command = ["docker", "login", "--username", "AWS", "--password-stdin", ecr_image_uri.split("/")[0]]
    subprocess.run(docker_login_command, input=password, text=True, check=True)

def cloudwatch_log_url(env, worker=False):
    log_name_key = "worker_log_group_name" if worker else "web_log_group_name"
    cloudwatch_log_group_name = get_terraform_output(log_name_key, env)
    return f"https://{AWS_REGION}.console.aws.amazon.com/cloudwatch/home?region={AWS_REGION}#logsV2:log-groups/log-group/{cloudwatch_log_group_name}"



def main():
    parser = argparse.ArgumentParser(prog="python deploy.py")
    parser.add_argument("env", help="Terraform environment to deploy")
    parser.add_argument("--no-input", action="store_true",
                        help="Skips request for confirmation before starting the deploy.")
    parser.add_argument("--skip-build", action="store_true",
                        help="Skips the build step and uses the existing ECR image for the environment.")
    parser.add_argument("--use-latest", action="store_true",
                        help="Skips the build step and uses the ECR image tagged `latest`.")
    parser.add_argument("--use-image-from-env",
                        help="If provided, skips the terraform build and instead uses the existing built image from the specified environment")
    parser.add_argument("--skip-migration", action="store_true", help="Skips the migration step.")
    parser.add_argument("--profile", help="Set the AWS profile name for the environment", default=AWS_PROFILE_NAME)
    parser.add_argument("--use-remote-cache", action="store_true",
                        help="During build step, uses the registry cache instead of the local cache")
    parser.set_defaults(func=deploy)

    subparsers = parser.add_subparsers(title="Extra utilities", prog="python deploy.py <ENV_NAME>")
    ssh_parser = subparsers.add_parser("ssh",
                                       help="SSH into running container in env instead of deploying")
    # START_FEATURE celery
    ssh_parser.add_argument("--web", action="store_true",
                            help="SSH into the web task rather than the worker task")
    # END_FEATURE celery
    ssh_parser.set_defaults(func=ssh)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    boto3.setup_default_session(profile_name=args.profile, region_name=AWS_REGION)
    args.func(args)


if __name__ == "__main__":
    main()
