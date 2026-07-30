variable "hostname" {
  type = string
}

variable "environment_name" {
  type = string
}

variable "load_balancer_arn" {
  type = string
}

variable "load_balancer_security_group_id" {
  type = string
}

variable "listener_arn" {
  type = string
}

variable "eb_application_name" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "vpc_private_subnet_ids" {
  type = list
}

variable "instance_type" {
  type = string
  default = "t3.small"
}

variable "deployment_policy" {
  type = string
  default = "AllAtOnce"
}

variable "num_processes" {
  type = number
  default = 1
}

variable "min_instances" {
  type = number
  default = 1
}

variable "max_instances" {
  type = number
  default = 1
}

variable "cname_prefix" {
  type = string
  default = ""
}

variable "certificate_arn" {
  type = string
  default = ""
}

variable "create_worker" {
  type = bool
  default = false
}