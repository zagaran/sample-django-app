locals {
  infrastructure_secrets = [
    "DATABASE_URL",
    "SECRET_KEY",
    "AWS_STORAGE_BUCKET_NAME",
    "DEFAULT_FROM_EMAIL"
  ]
  
  config_secrets = [
    "ALLOWED_HOSTS",
    "GOOGLE_OAUTH2_KEY",
    "GOOGLE_OAUTH2_SECRET",
    "EC2_METADATA",
  ]

  app_env_name = "${var.application_name}-${var.environment_name}"

  ecs_infrastructure_secrets = [
    for setting in local.infrastructure_secrets :
    {
      name : setting
      valueFrom : format("%s:%s::", aws_secretsmanager_secret.web_infrastructure.arn, setting)
    }
  ]

  ecs_config_secrets = [
    for setting in local.config_secrets :
    {
      name : setting
      valueFrom : format("%s:%s::", data.aws_secretsmanager_secret.web_config.arn, setting)
    }
  ]

  ecs_secrets = concat(local.ecs_infrastructure_secrets, local.ecs_config_secrets)
}