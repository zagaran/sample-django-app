resource "aws_secretsmanager_secret" "web_config" {
  name = "${local.app_env_name}-web-config"
}

data "aws_secretsmanager_secret_version" "web_config" {
  secret_id = aws_secretsmanager_secret.web_config.id
}

resource "aws_secretsmanager_secret" "web_infrastructure" {
  name = "${local.app_env_name}-web-infrastructure"
}

resource "aws_secretsmanager_secret_version" "web_infrastructure" {
  secret_id = aws_secretsmanager_secret.web_infrastructure.id
  secret_string = jsonencode({
    ALLOWED_HOSTS           = var.application_url
    AWS_STORAGE_BUCKET_NAME = aws_s3_bucket.bucket.id
    DATABASE_URL = format(
      "postgres://dbuser:%s@%s:5432/%s?sslmode=require",
      random_password.db_password.result,
      aws_db_instance.database.address,
      aws_db_instance.database.db_name
    )
    REMOTE_REPO_NAME  = var.remote_repo_name
    SECRET_KEY        = random_password.app_secret_key.result
    CELERY_BROKER_URL = "redis://${aws_elasticache_replication_group.redis.primary_endpoint_address}:${aws_elasticache_replication_group.redis.port}"
    # SES
    DEFAULT_FROM_EMAIL = var.default_from_email
  })
}

resource "random_password" "app_secret_key" {
  length  = 32
  special = false
}