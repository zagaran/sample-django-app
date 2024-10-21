# Required Variables
environment_name = "staging"
aws_profile_name = ""  # TODO: FILL ME IN
aws_region = ""  # TODO: FILL ME IN
terraform_backend_bucket = ""  # TODO: FILL ME IN
vpc_id = ""  # TODO: FILL ME IN
web_config_secret_name = ""  # TODO: FILL ME IN
s3_bucket_prefix = ""  # TODO: FILL ME IN
rds_engine_version = ""  # TODO: FILL ME IN
ses_identity = ""  # TODO: FILL ME IN
ses_from_email = ""  # TODO: FILL ME IN
certificate_manager_arn =  ""  # TODO: FILL ME IN

# Optional Variables
rds_backup_retention_period = 10
rds_deletion_protection = true
rds_instance_class = "db.t3.micro"
rds_multi_az = false
container_web_cpu = 256
container_web_memory = 1024
container_count = 1
ssl_policy = "ELBSecurityPolicy-TLS13-1-2-Res-FIPS-2023-04"
