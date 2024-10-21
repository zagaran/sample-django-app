variable "environment_name" {
  type = string
}

variable "application_name" {
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

variable "rds_backup_retention_period" {
  type = number
}

variable "rds_deletion_protection" {
  type = bool
}

variable "rds_engine_version" {
  type = string
}

variable "rds_instance_class" {
  type = string
}

variable "rds_multi_az" {
  type = bool
}
