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
    var1 = "x"
    var2 = "y"
}


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
