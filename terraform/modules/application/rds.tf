resource "random_password" "db_password" {
  length  = 50
  special = false
}

resource "aws_db_instance" "database" {
  allocated_storage           = 20
  allow_major_version_upgrade = true
  apply_immediately           = true
  backup_retention_period     = var.rds_backup_retention_period
  db_name                     = format("%s_db", replace(var.application_name, "-", "_"))
  deletion_protection         = var.rds_deletion_protection
  skip_final_snapshot         = !var.rds_deletion_protection
  engine                      = "postgres"
  engine_version              = var.rds_engine_version
  identifier                  = "${local.app_env_name}-db"
  instance_class              = var.rds_instance_class
  multi_az                    = var.rds_multi_az
  password                    = random_password.db_password.result
  storage_encrypted           = true
  storage_type                = "gp2"
  username                    = "dbuser"
  publicly_accessible         = false
  vpc_security_group_ids      = [aws_security_group.database.id]
  db_subnet_group_name        = aws_db_subnet_group.database.name
}

resource "aws_db_subnet_group" "database" {
  name = "${local.app_env_name}-database-subnets"
  subnet_ids = [
    aws_subnet.public_subnet_a.id,
    aws_subnet.public_subnet_b.id
  ]
}