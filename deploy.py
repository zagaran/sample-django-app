import argparse
import logging
import subprocess
import sys
import time

import boto3.session

AWS_REGION = "us-east-1"
AWS_PROFILE_NAME = "FILL ME IN"

MIGRATION_TIMEOUT_SECONDS = 10 * 60  # Ten minutes


class MigrationFailed(Exception):
    pass


class MigrationTimeOut(Exception):
    pass

parser = argparse.ArgumentParser()
parser.add_argument("--no-input", action="store_true", help="Skips request for confirmation before starting the deploy.")
parser.add_argument("--skip-build", action="store_true", help="Skips the build step and uses the existing ECR image.")
parser.add_argument("--use-image-from-env", help="If provided, skips the terraform build and instead uses the existing built image from the specified environment")
parser.add_argument("--skip-migration", action="store_true", help="Skips the migration step.")
parser.add_argument("-env", help="Terraform environment to deploy", required=True)


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

    # Refresh terraform state
    logging.info("Refreshing terraform state...")
    subprocess.run(["terraform", "refresh"], cwd=f"terraform/envs/{args.env}", check=True, capture_output=True)

    # ECR image setup
    if args.use_image_from_env:
        subprocess.run(["terraform", "refresh"], cwd=f"terraform/envs/{args.use_image_from_env}", check=True, capture_output=True)
        copy_image_from_env(args.use_image_from_env, args.env)
    elif not args.skip_build:
        build_and_push_image(args.env)

    if not args.skip_migration:
        # Run and wait for migrations
        run_migrations(args.env)

    # Redeploy services
    restart_web_service(args.env)

    logging.info("Deployment complete.")


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
    ecr_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecr")
    # Get image manifest
    image_response = ecr_client.batch_get_image(
        repositoryName=from_ecr_repository_name,
        imageIds=[{
            "imageTag": from_env
        }],
        acceptedMediaTypes=["string"]
    )

    image_manifest = image_response["images"][0]["imageManifest"]
    image_manifest_media_type = image_response["images"][0]["imageManifestMediaType"]
    # Add new tag to manifest
    to_ecr_repository_name = get_terraform_output("ecr_repository_name", to_env)
    ecr_client.put_image(
        repositoryName=to_ecr_repository_name,
        imageManifest=image_manifest,
        imageTag=to_env,
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
    status_check_interval = 30  # Check migration status at interval (in seconds)

    while time.time() - start < MIGRATION_TIMEOUT_SECONDS:
        logging.info("Waiting for migrations to finish...")
        describe_tasks_response = ecs_client.describe_tasks(cluster=cluster_id, tasks=[migration_task_id])
        task = describe_tasks_response["tasks"][0]
        stop_code = task.get("stopCode")
        if not stop_code:
            time.sleep(status_check_interval)
            continue
        if stop_code == "EssentialContainerExited":
            # The migration task has finished successfully
            logging.info("Migration complete")
            return
        logging.error("Migration task failed.")
        raise MigrationFailed()
    logging.error("Migration timed out. It may still be running.")
    raise MigrationTimeOut()


def restart_web_service(env):
    # Restart ECS web service to deploy new code
    ecs_client = boto3.session.Session(profile_name=AWS_PROFILE_NAME, region_name=AWS_REGION).client("ecs")
    logging.info("Redeploying web service...")
    ecs_client.update_service(
        cluster=get_terraform_output("cluster_id", env),
        service=get_terraform_output("web_service_name", env),
        forceNewDeployment=True
    )


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(levelname)s - %(message)s")
    deploy(args)


