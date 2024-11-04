locals {
  app_env_name = "${var.application_name}-${var.environment_name}"

  ecs_infrastructure_secrets = [
    for setting in keys(jsondecode(nonsensitive(aws_secretsmanager_secret_version.web_infrastructure.secret_string))) :
    {
      name : setting
      valueFrom : format("%s:%s::", aws_secretsmanager_secret.web_infrastructure.arn, setting)
    }
  ]

  ecs_config_secrets = [
    for setting in keys(jsondecode(nonsensitive(data.aws_secretsmanager_secret_version.web_config.secret_string))) :
    {
      name : setting
      valueFrom : format("%s:%s::", data.aws_secretsmanager_secret.web_config.arn, setting)
    }
  ]

  ecs_secrets = concat(local.ecs_infrastructure_secrets, local.ecs_config_secrets)
}