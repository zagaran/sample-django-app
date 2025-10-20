resource "aws_ecr_repository" "ecr" {
  name = "${local.app_env_name}-ecr"
}