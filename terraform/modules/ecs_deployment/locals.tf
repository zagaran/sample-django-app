data "aws_caller_identity" "current" {}

locals {
  app_env_name = "${var.application_name}-${var.environment_name}"

  ecr_image_uri = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${data.aws_region.current.name}.amazonaws.com/${var.ecr_repository_name}:${var.environment_name}"

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

  # If different web and worker config is needed, split this into web- and worker-
  ecs_secrets = concat(local.ecs_infrastructure_secrets, local.ecs_config_secrets)

  ecs_worker_command = split(" ", "celery -A config worker --beat --scheduler redbeat.RedBeatScheduler --loglevel=INFO")
}