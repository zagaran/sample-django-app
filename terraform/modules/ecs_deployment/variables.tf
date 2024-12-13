# Required Variables
variable "application_name" {
  type = string
}

variable "environment_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "web_config_secret_name" {
  type = string  # key for secrets_manager secrets that are not terraform managed
}

variable "s3_bucket_prefix" {
  type = string
}

variable "rds_engine_version" {
  type = string
}

variable "ses_identity" {
  type = string
}

variable "ses_from_email" {
  type = string
}

variable "certificate_manager_arn" {
  type = string
}

variable "ecr_repository_name" {
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

variable "container_web_cpu" {
  type = number
  default = 256
}

variable "container_web_memory" {
  type = number
  default = 1024
}

variable "container_web_count" {
  type = number
  default = 1
}

variable "container_worker_cpu" {
  type = number
  default = 256
}

variable "container_worker_memory" {
  type = number
  default = 1024
}

variable "container_worker_count" {
  type = number
  default = 1
}

variable "ssl_policy" {
  type = string
  default = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
}

variable "redis_instance_type" {
  type = string
  default = "cache.t3.micro"
}
