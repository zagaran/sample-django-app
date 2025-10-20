# --------------------------------- REQUIRED --------------------------------- #


variable "environment" {
  type = string
}

variable "application_name" {
  type = string
}

variable "application_url" {
  type = string
}

variable "data_application_domain" {
  type = string
}

variable "data_email_domain" {
  type = string
}

variable "remote_repo_name" {
  type = string
}

# --------------------------------- OPTIONAL --------------------------------- #


variable "rds_backup_retention_period" {
  type    = number
  default = 30
}

variable "rds_deletion_protection" {
  type    = bool
  default = true
}

variable "rds_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "rds_multi_az" {
  type    = bool
  default = false
}

variable "rds_engine_version" {
  type    = string
  default = "17"
}

variable "container_web_cpu" {
  type    = number
  default = 256
}

variable "container_web_count" {
  type    = number
  default = 1
}

variable "container_worker_cpu" {
  type    = number
  default = 256
}

variable "container_worker_count" {
  type    = number
  default = 1
}

variable "redis_instance_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "redis_engine_version" {
  type    = string
  default = "7.1"
}

variable "github_oidc_provider_arn" {
  type    = string
  default = ""
}

variable "fargate_web_cpu" {
  type    = number
  default = 1024
}

variable "fargate_web_memory" {
  type    = number
  default = 2048
}

variable "fargate_worker_cpu" {
  type    = number
  default = 1024
}

variable "fargate_worker_memory" {
  type    = number
  default = 2048
}

variable "web_desired_count" {
  type    = number
  default = 1
}

variable "worker_desired_count" {
  type    = number
  default = 1
}

variable "ssl_policy" {
  type    = string
  default = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
}

variable "load_balancer_deletion_protection" {
  type    = bool
  default = true
}

variable "load_balancer_idle_timeout" {
  type    = number
  default = 60
}

variable "default_from_email" {
  type    = string
  default = "noreply@test.com"
}