resource "aws_secretsmanager_secret" "web_infrastructure" {
  name = "${local.app_env_name}-web-infrastructure"
}

resource "aws_secretsmanager_secret_version" "web_infrastructure" {
  secret_id = aws_secretsmanager_secret.web_infrastructure.id
  secret_string = jsonencode({
    AWS_STORAGE_BUCKET_NAME = aws_s3_bucket.bucket.id
    DATABASE_URL = format(
      "postgres://dbuser:%s@%s:5432/database?sslmode=require",
      random_password.db_password.result,
      aws_db_instance.database.address,
    )
    DEFAULT_FROM_EMAIL = var.ses_from_email
    SECRET_KEY = random_password.app_secret_key.result
  })
}


data "aws_secretsmanager_secret" "web_config" {
  name = var.web_config_secret_name
}


data "aws_secretsmanager_secret_version" "web_config" {
  secret_id = data.aws_secretsmanager_secret.web_config.id
}


resource "random_password" "app_secret_key" {
  length  = 32
  special = false
}
