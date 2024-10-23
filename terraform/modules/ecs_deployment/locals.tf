locals {
  app_env_name = "${var.application_name}-${var.environment_name}"

  ecs_secrets = [
    {
      name : "ALLOWED_HOSTS",
      valueFrom : format("%s:ALLOWED_HOSTS::", aws_secretsmanager_secret.web_infrastructure.arn)
    },
    {
      name : "DATABASE_URL",
      valueFrom : format("%s:DATABASE_URL::", aws_secretsmanager_secret.web_infrastructure.arn)
    },
    {
      name : "SECRET_KEY",
      valueFrom : format("%s:SECRET_KEY::", aws_secretsmanager_secret.web_infrastructure.arn)
    },
    {
      name : "AWS_STORAGE_BUCKET_NAME",
      valueFrom : format("%s:AWS_STORAGE_BUCKET_NAME::", aws_secretsmanager_secret.web_infrastructure.arn)
    },
    {
      name : "DEFAULT_FROM_EMAIL",
      valueFrom : format("%s:DEFAULT_FROM_EMAIL::", aws_secretsmanager_secret.web_infrastructure.arn)
    },
    {
      name : "GOOGLE_OAUTH2_KEY",
      valueFrom : format("%s:GOOGLE_OAUTH2_KEY::", data.aws_secretsmanager_secret.web_config.arn)
    },
    {
      name : "GOOGLE_OAUTH2_SECRET",
      valueFrom : format("%s:GOOGLE_OAUTH2_SECRET::", data.aws_secretsmanager_secret.web_config.arn)
    },
  ]
}