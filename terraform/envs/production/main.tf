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
    vpc_id = ""  # TODO: FILL ME IN
    web_config_secret_name = ""  # TODO: FILL ME IN
    s3_bucket_prefix = ""  # TODO: FILL ME IN
    rds_engine_version = ""  # TODO: FILL ME IN
    ses_identity = ""  # TODO: FILL ME IN
    ses_from_email = ""  # TODO: FILL ME IN
    certificate_manager_arn =  ""  # TODO: FILL ME IN
    ecr_repository_name =  ""  # TODO: FILL ME IN
    ecr_image_uri = ""  # TODO: FILL ME IN

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