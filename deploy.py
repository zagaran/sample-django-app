import argparse
import logging
import subprocess
import sys
import time

import boto3.session

AWS_REGION = "us-east-1"
AWS_PROFILE_NAME = "FILL ME IN"

MIGRATION_TIMEOUT_SECONDS = 10 * 60  # Ten minutes
STATUS_CHECK_INTERVAL = 30


class MigrationFailed(Exception):
    pass


class MigrationTimeOut(Exception):
    pass


def deploy(args):
    if not args.no_input:
        # Request user confirmation
        confirmation_message = f"\nBegin deploying to {args.env}? "
        if args.use_image_from_env:
            confirmation_message += f"This will use the current {args.use_image_from_env} deployment. "
        confirmation_message += "(y/n): "
        confirmation = input(confirmation_message)
        if confirmation.lower() not in ["y", "yes"]:
            logging.warning("Deployment canceled.")
            return

    # Local state setup for relevant envs
    terraform_envs = [args.env]
    if args.use_image_from_env:
        terraform_envs.append(args.use_image_from_env)
    setup(terraform_envs)

    # ECR image setup
    if args.use_image_from_env:
        subprocess.run(["terraform", "refresh"], cwd=f"terraform/envs/{args.use_image_from_env}", check=True, capture_output=True)
        copy_image_from_env(args.use_image_from_env, args.env)
    elif args.use_latest:
        copy_latest_image(args.env)
    elif not args.skip_build:
        build_and_push_image(args.env)
    else:
        logging.info("Skipping build step")

    if args.skip_migration:
        logging.info("Skipping database migration")
    else:
        # Run and wait for migrations
        run_migrations(args.env)

    # Redeploy services
    restart_web_service(args.env)


def setup(envs):
    # Refresh terraform state
    logging.info("Refreshing terraform state...")
    for env in envs:
        subprocess.run(["terraform", "refresh"], cwd=f"terraform/envs/{env}", check=True, capture_output=True)


def subprocess_output(command_args, **subprocess_kwargs):
    output = subprocess.run(command_args, **subprocess_kwargs, capture_output=True, check=True)
    return output.stdout.decode('utf-8').strip("\n").strip('"')


def get_terraform_output(output_key, env):
    return subprocess_output(["terraform", "output", output_key], cwd=f"terraform/envs/{env}")


def build_and_push_image(env):
    # Build and tag image
    ecr_repository_name = get_terraform_output("ecr_repository_name", env)
    ecr_image_uri = get_terraform_output("ecr_image_uri", env)
    logging.info("Building docker image...")
    build_command = ["docker", "build", "-t", ecr_repository_name, "."]
    subprocess.run(build_command, check=True)
    subprocess.run(["docker", "tag", f"{ecr_repository_name}:latest", ecr_image_uri], check=True)

    # Push image to ECR
    logging.info("Logging in to ECR...")
    password_command = ["aws", "ecr", "get-login-password", "--region", AWS_REGION, "--profile", AWS_PROFILE_NAME]
    password = subprocess_output(password_command)
    docker_login_command = ["docker", "login", "--username", "AWS", "--password-stdin", ecr_image_uri.split("/")[0]]
    subprocess.run(docker_login_command, input=password, text=True, check=True)
    logging.info("Pushing docker image to ECR...")
    subprocess.run(["docker", "push", ecr_image_uri], check=True)

    # Remove unused docker images to preserve local disk space
    subprocess.run(["docker", "image", "prune", "-f"])


def copy_image_from_env(from_env, to_env):
    # Retags image from from_env into to_env.
    logging.info(f"Copying image from {from_env} to {to_env}")
    from_ecr_repository_name = get_terraform_output("ecr_repository_name", from_env)
    to_ecr_repository_name = get_terraform_output("ecr_repository_name", to_env)
    retag_image(from_ecr_repository_name, from_env, to_ecr_repository_name, to_env)


def copy_latest_image(env):
    # Retags latest image in repository for use by env
    logging.info(f"Copying latest image to {env}")
    ecr_repository_name = get_terraform_output("ecr_repository_name", env)
    retag_image(ecr_repository_name, "latest", ecr_repository_name, env)


def retag_image(from_repository, from_tag, to_repository, to_tag):
    ecr_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecr")
    # Get image manifest
    image_response = ecr_client.batch_get_image(
        repositoryName=from_repository,
        imageIds=[{
            "imageTag": from_tag
        }],
        acceptedMediaTypes=["string"]
    )
    image_manifest = image_response["images"][0]["imageManifest"]
    image_manifest_media_type = image_response["images"][0]["imageManifestMediaType"]
    # Add new tag to manifest
    ecr_client.put_image(
        repositoryName=to_repository,
        imageManifest=image_manifest,
        imageTag=to_tag,
        imageManifestMediaType=image_manifest_media_type,
    )


def run_migrations(env):
    # Runs a migration task using the web server task definition with an overridden command
    cluster_id = get_terraform_output("cluster_id", env)
    ecs_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecs")
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

    while time.time() - start < MIGRATION_TIMEOUT_SECONDS:
        logging.info("Waiting for migrations to finish...")
        describe_tasks_response = ecs_client.describe_tasks(cluster=cluster_id, tasks=[migration_task_id])
        task = describe_tasks_response["tasks"][0]
        stop_code = task.get("stopCode")
        if not stop_code:
            time.sleep(STATUS_CHECK_INTERVAL)
            continue
        if stop_code == "EssentialContainerExited":
            # The migration task has finished successfully
            logging.info("Migration complete")
            return
        logging.error(f"Migration task failed with code {stop_code} and reason {task.get('stoppedReason')}.")
        raise MigrationFailed()
    logging.error("Migration timed out. It may still be running.")
    raise MigrationTimeOut()


def restart_web_service(env):
    # Restart ECS web service to deploy new code
    ecs_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecs")
    logging.info("Redeploying web service...")
    cluster_id = get_terraform_output("cluster_id", env)
    service_name = get_terraform_output("web_service_name", env)
    ecs_client.update_service(
        cluster=cluster_id,
        service=service_name,
        forceNewDeployment=True
    )

    while True:
        logging.info("Waiting for deployment to finish...")
        services_response = ecs_client.describe_services(cluster=cluster_id, services=[service_name])
        deployments = services_response["services"][0]["deployments"]
        new_deployment = next(deployment for deployment in deployments if deployment["status"] == "PRIMARY")
        deployment_state = new_deployment["rolloutState"]
        if deployment_state == "IN_PROGRESS":
            time.sleep(STATUS_CHECK_INTERVAL)
            continue
        if deployment_state == "COMPLETED":
            logging.info("Success! Deployment complete.")
        elif deployment_state == "FAILED":
            logging.error(f"Deployment failed! Reason: {new_deployment['rolloutStateReason']}")
        else:
            logging.warning(f"Unknown deployment state {deployment_state}. Please check the console.")
        break



def ssh(args):
    # Runs a bash shell in a running task for the env. Note this may run in a short-lived task (e.g. migration task)
    # Refresh terraform state
    setup([args.env])
    cluster_id = get_terraform_output("cluster_id", args.env)
    service_name = get_terraform_output("web_service_name", args.env)
    ecs_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecs")
    list_tasks_resp = ecs_client.list_tasks(cluster=cluster_id, serviceName=service_name)
    task_ids = list_tasks_resp["taskArns"]

    if task_ids:
        task_id = task_ids[0]
        bash_command = ["aws", "ecs", "execute-command", "--cluster", cluster_id, "--task", task_id,
                        "--region", AWS_REGION, "--profile", AWS_PROFILE_NAME, "--interactive",
                        "--command", "'/bin/bash'"]
        subprocess.run(bash_command)



def main():
    parser = argparse.ArgumentParser(prog="python deploy.py")
    parser.add_argument("--no-input", action="store_true",
                        help="Skips request for confirmation before starting the deploy.")
    parser.add_argument("--skip-build", action="store_true",
                        help="Skips the build step and uses the existing ECR image for the environment.")
    parser.add_argument("--use-latest", action="store_true",
                        help="Skips the build step and uses the ECR image tagged `latest`.")
    parser.add_argument("--use-image-from-env",
                        help="If provided, skips the terraform build and instead uses the existing built image from the specified environment")
    parser.add_argument("--skip-migration", action="store_true", help="Skips the migration step.")
    parser.add_argument("-env", help="Terraform environment to deploy", required=True)
    parser.set_defaults(func=deploy)

    subparsers = parser.add_subparsers(title="Extra utilities", prog="python deploy.py -env <ENV_NAME>")
    ssh_parser = subparsers.add_parser("ssh", help="SSH into running container in env instead of deploying")
    ssh_parser.set_defaults(func=ssh)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    args.func(args)


if __name__ == "__main__":
    main()
