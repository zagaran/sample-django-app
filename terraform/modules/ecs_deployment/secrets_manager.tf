resource "aws_secretsmanager_secret" "web_infrastructure" {
  name = format("%s-infrastructure", var.environment_name)
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

resource "random_password" "app_secret_key" {
  length  = 32
  special = false
}