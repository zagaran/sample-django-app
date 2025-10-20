data "aws_caller_identity" "current" {}

locals {
  app_env_name = "${var.application_name}-${var.environment}"

  ecr_image_uri = format(
    "%s.dkr.ecr.%s.amazonaws.com/%s:latest",
    data.aws_caller_identity.current.account_id,
    data.aws_region.current.name,
    aws_ecr_repository.ecr.name,
  )
  ecr_repository_arn = format(
    "arn:aws:ecr:%s:%s:repository/%s",
    data.aws_region.current.name,
    data.aws_caller_identity.current.account_id,
    aws_ecr_repository.ecr.name
  )
  ecs_cluster_arn = format(
    "arn:aws:ecs:%s:%s:repository/%s",
    data.aws_region.current.name,
    data.aws_caller_identity.current.account_id,
    aws_ecs_cluster.cluster.name
  )

  enable_github_oidc = var.github_oidc_provider_arn != null && var.github_oidc_provider_arn != ""

  ecs_infrastructure_secrets = [
    for setting in keys(jsondecode(nonsensitive(
      aws_secretsmanager_secret_version.web_infrastructure.secret_string,
    ))) :
    {
      name : setting
      valueFrom : format("%s:%s::", aws_secretsmanager_secret.web_infrastructure.arn, setting)
    }
  ]

  ecs_config_secrets = [
    for setting in keys(jsondecode(nonsensitive(
      data.aws_secretsmanager_secret_version.web_config.secret_string,
    ))) :
    {
      name : setting
      valueFrom : format("%s:%s::", data.aws_secretsmanager_secret_version.web_config.arn, setting)
    }
  ]

  ecs_secrets        = concat(local.ecs_infrastructure_secrets, local.ecs_config_secrets)
  ecs_worker_command = split(" ", "celery -A config worker --beat --scheduler redbeat.RedBeatScheduler --loglevel=INFO -E")
}