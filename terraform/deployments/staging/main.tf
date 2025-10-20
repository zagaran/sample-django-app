terraform {

  backend "s3" {
    profile = "zag-dev-cli"
    bucket  = "matthewzagarandev"
    key     = "staging/terraform.tfstate"
    region  = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.59"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "us-east-1"
  profile = "zag-dev-cli"
}

module "staging" {
  source = "../../modules/application"

  # --------------------------------- REQUIRED --------------------------------- #

  environment      = "staging"
  application_name = "deploy"
  application_url  = "staging-deploy.dev.zagaran.com"
  remote_repo_name = "zagaran/deploy"

  # ------------------------ References other resources ------------------------ #

  data_application_domain = "dev.zagaran.com"
  data_email_domain       = "dev.zagaran.com"

  # --------------------------------- OPTIONAL --------------------------------- #

  rds_deletion_protection           = false
  load_balancer_deletion_protection = false

}

output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = module.staging.cluster_id
}

output "ecr_image_uri" {
  description = "ECR URI where the environment's image is stored"
  value       = module.staging.ecr_image_uri
}

output "ecr_repository_name" {
  description = "The name of the ECR repository"
  value       = module.staging.ecr_repository_name
}

output "web_service_name" {
  description = "The name of the ECS web service. This is also the container name."
  value       = module.staging.web_service_name
}

output "web_network_configuration_security_group" {
  description = "The security group used by the ECS web task"
  value       = tolist(module.staging.web_network_configuration_security_groups)[0]
}

output "web_network_configuration_subnet" {
  description = "The ID of one the subnets used by the web task"
  value       = tolist(module.staging.web_network_configuration_subnets)[0]
}

output "web_task_definition_arn" {
  description = "The ARN of the ECS web service task definition"
  value       = module.staging.web_task_definition_arn
}

output "web_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value       = module.staging.web_log_group_name
}

output "worker_service_name" {
  description = "The name of the ECS worker service. This is also the container name."
  value       = module.staging.worker_service_name
}

output "worker_task_desired_count" {
  description = "The intended number of worker tasks"
  value       = module.staging.worker_task_desired_count
}

output "worker_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value       = module.staging.worker_log_group_name
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = module.staging.s3_bucket_name
}