locals {
  app_env_name = "${var.application_name}-${var.environment_name}"

  ecs_secrets_map = {
    DATABASE_URL           = "${aws_secretsmanager_secret.web_infrastructure.arn}:DATABASE_URL::"
    SECRET_KEY             = "${aws_secretsmanager_secret.web_infrastructure.arn}:SECRET_KEY::"
    AWS_STORAGE_BUCKET_NAME = "${aws_secretsmanager_secret.web_infrastructure.arn}:AWS_STORAGE_BUCKET_NAME::"
    DEFAULT_FROM_EMAIL     = "${aws_secretsmanager_secret.web_infrastructure.arn}:DEFAULT_FROM_EMAIL::"
  }

  ecs_secrets = [
    for key, value in local.ecs_secrets_map : {
      name      = key
      valueFrom = value
    }
  ]
}