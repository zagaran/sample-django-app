terraform {

  backend "s3" {
    profile = "zag-dev-cli"
    bucket  = "matthewzagarandev"
    key     = "shared/terraform.tfstate"
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

module "shared" {
  source = "../../modules/shared"

  # --------------------------------- REQUIRED --------------------------------- #

  environment     = "shared"
  application_url = "staging-deploy.zagaran.com"
}