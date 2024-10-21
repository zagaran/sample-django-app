variable "environment_name" {
  type string
}

variable "vpc_id" {
  type string
}

variable "web_config_secret_name" {
  type string
}

variable "s3_bucket_prefix" {
  type string
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
  type string
}

variable "rds_multi_az" {
  type bool
}

variable "ses_identity" {
  type string
}

variable "ses_from_email" {
  type string
}

variable "ecr_image_uri" {
  type string
}

variable "container_web_cpu" {
  type number
}

variable "container_web_memory" {
  type number
}

variable "container_count" {
  type number
}