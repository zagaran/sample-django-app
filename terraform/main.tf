terraform {
  backend "s3" {
    bucket = var.terraform_backend_bucket
    key = format("%.tfstate" % var.environment_name)
    region = var.aws_region
    profile = var.aws_profile_name
  }
  
  required_providers {
    aws = {
      source = "hasicorp/aws"
      version = "~>5.59"
    }
  }
}

provider "aws" {
  region = var.aws_region
  profile = var.aws_profile_name
}

module "ecs_deployment" {
    source = "./modules/ecs_deployment"
    
    environment = var.environment_name
    vpc_id = var.vpc_id
    web_config_secret_name = var.web_config_secret_name
    s3_bucket_prefix = var.s3_bucket_prefix
    rds_engine_version = var.rds_engine_version
    rds_backup_retention_period = var.rds_backup_retention_period
    rds_deletion_protection = var.rds_deletion_protection
    rds_instance_class = var.rds_instance_class
    rds_multi_az = var.rds_multi_az
}

# Required Variables
variable "aws_profile_name" {
  type = string
}

variable "aws_region" {
  type = string
  default = "us-east-1"
}

variable "environment_name" {
  type = string
}

variable "terraform_backend_bucket" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "web_config_secret_name" {
  type = string
}

variable "s3_bucket_prefix" {
  type = string
}

variable "rds_engine_version" {
  type = string
}


# Optional Variables
variable "rds_backup_retention_period" {
  type = number
  default = 30
}

variable "rds_deletion_protection" {
  type = bool
  default = true
}

variable "rds_instance_class" {
  type = string
  default = "db.t3.micro"
}

variable "rds_multi_az" {
  type = bool
  default = false
}
