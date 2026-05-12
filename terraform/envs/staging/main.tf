terraform {
  backend "s3" {
    bucket = ""  # TODO: FILL ME IN
    key = "staging.tfstate"
    region = "us-east-1"  # TODO: FILL ME IN
    profile = "sample-django-app"  # TODO: FILL ME IN
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~>5.100"
    }
  }
}

provider "aws" {
  region = "us-east-1"  # TODO: FILL ME IN
  profile = "sample-django-app"  # TODO: FILL ME IN
}

module "ecs_deployment" {
    source = "../../modules/ecs_deployment"

    # Required Variables
    environment_name = "staging"  # Should match directory name
    application_name = "sample-django-app"  # Base application slug for resource naming
    vpc_id = ""  # TODO: VPCs -> VPC ID
    web_config_secret_name = ""  # TODO: Secrets Manager -> Store a new secret -> Secret name
    s3_bucket_prefix = ""  # TODO: Base slug for S3 bucket names (unique among applications, shared among environments)
    rds_engine_version = ""  # TODO: Desired Postgres major version, e.g. "18"
    ses_from_email = ""  # TODO: Desired sending email within the provided SES identity
    certificate_manager_arn =  ""  # TODO: Certificate manager -> Request -> ARN
    ecr_repository_name =  ""  # TODO: ECR -> Create repository -> Repository name

    # Optional Variables
    rds_backup_retention_period = 10
    rds_deletion_protection = true
    rds_instance_class = "db.t3.micro"
    rds_multi_az = false
    container_web_cpu = 256
    container_web_memory = 1024
    container_web_count = 1
    ssl_policy = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
}

output "cluster_id" {
  description = "The ID of the ECS cluster"
  value = module.ecs_deployment.cluster_id
}

output "ecr_image_uri" {
  description = "ECR URI where the environment's image is stored"
  value = module.ecs_deployment.ecr_image_uri
}

output "ecr_repository_name" {
  description = "The name of the ECR repository"
  value = module.ecs_deployment.ecr_repository_name
}

output "public_ip" {
  description = "The public IP address of the load balancer for the web service"
  value = module.ecs_deployment.public_ip
}

output "web_service_name" {
  description = "The name of the ECS web service. This is also the container name."
  value = module.ecs_deployment.web_service_name
}

output "web_network_configuration_security_group" {
  description = "The security group used by the ECS web task"
  value = tolist(module.ecs_deployment.web_network_configuration_security_groups)[0]
}

output "web_network_configuration_subnet" {
  description = "The ID of one the subnets used by the web task"
  value = tolist(module.ecs_deployment.web_network_configuration_subnets)[0]
}

output "web_task_definition_arn" {
  description = "The ARN of the ECS web service task definition"
  value = module.ecs_deployment.web_task_definition_arn
}

output "web_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value = module.ecs_deployment.web_log_group_name
}
# START_FEATURE celery
output "worker_service_name" {
  description = "The name of the ECS worker service. This is also the container name."
  value = module.ecs_deployment.worker_service_name
}

output "worker_task_desired_count" {
  description = "The intended number of worker tasks"
  value = module.ecs_deployment.worker_task_desired_count
}

output "worker_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value = module.ecs_deployment.worker_log_group_name
}
# END_FEATURE celery