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
      verison = "~>5.59"
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
    ses_identity = var.ses_identity
    ses_from_email = var.ses_from_email
    container_web_cpu = var.container_web_cpu
    container_web_memory = var.container_web_memory
    container_count = var.container_web_memory
    certificate_manager_arn = var.certificate_manager_arn
    ssl_policy = var.ssl_policy
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

variable "ses_identity" {
  type string
}

variable "ses_from_email" {
  type string
}

variable "certificate_manager_arn" {
  type string
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
  type string
  default = "db.t3.micro"
}

variable "rds_multi_az" {
  typr bool
  default = false
}

variable "container_web_cpu" {
  type number
  default 256
}

variable "container_web_memory" {
  type number
  default = 1024
}

variable "container_count" {
  type number
  default 1
}

variable "ssl_policy" {
  type string
  default = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
}
