terraform {
  backend "s3" {
    bucket = ""  # TODO: FILL ME IN
    key = "production.tfstate"
    region = "us-east-1"  # TODO: FILL ME IN
    profile = ""  # TODO: FILL ME IN
  }
  
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~>5.59"
    }
  }
}

provider "aws" {
  region = "us-east-1"  # TODO: FILL ME IN
  profile = ""  # TODO: FILL ME IN
}

module "ecs_deployment" {
    source = "../../modules/ecs_deployment"
    
    # Required Variables
    environment_name = "production"
    application_name = ""  # TODO: FILL ME IN
    vpc_id = ""  # TODO: FILL ME IN
    web_config_secret_name = ""  # TODO: FILL ME IN
    s3_bucket_prefix = ""  # TODO: FILL ME IN
    rds_engine_version = ""  # TODO: FILL ME IN
    ses_identity = ""  # TODO: FILL ME IN
    ses_from_email = ""  # TODO: FILL ME IN
    certificate_manager_arn =  ""  # TODO: FILL ME IN
    ecr_repository_name =  ""  # TODO: FILL ME IN

    # Optional Variables
    rds_backup_retention_period = 30
    rds_deletion_protection = true
    rds_instance_class = "db.m7g.large"
    rds_multi_az = true
    container_web_cpu = 1024
    container_web_memory = 1024
    container_count = 2
    ssl_policy = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
}

output "cluster_id" {
  description = "The ID of the ECS cluster"
  value = module.ecs_deployment.cluster_id
}

output "cloudwatch_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value = module.ecs_deployment.cloudwatch_log_group_name
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
  description = "The name of the ECS container running the web service"
  value = module.ecs_deployment.web_service_name
}

output "web_network_configuration_security_group" {
  description = "The security groups used by the ECS web task"
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
