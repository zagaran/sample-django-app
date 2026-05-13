variable "role_name" {
  type = string
  default = "github-actions-deployment-role"
}

variable "github_repo_owner_name" {
  type = string
  description = "Name of the GitHub organization/user who owns the repo for this code"
}

variable "github_repo_name" {
  type = string
  description = "Name of the GitHub repo for this code"
}