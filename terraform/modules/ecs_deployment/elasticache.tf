resource "aws_elasticache_replication_group" "redis" {
  replication_group_id        = "${local.app_env_name}-redis"
  description                 = "Redis replication group"
  apply_immediately           = true
  auto_minor_version_upgrade  = true
  automatic_failover_enabled  = true
  engine_version              = "7.1"
  node_type                   = var.redis_instance_type
  num_cache_clusters          = 2
  port                        = 6379
  preferred_cache_cluster_azs = ["us-east-1a", "us-east-1b"]
  security_group_ids          = [aws_security_group.redis.id]
  subnet_group_name           = aws_elasticache_subnet_group.redis.name

  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis_log_group.name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "engine-log"
  }
}

resource "aws_elasticache_subnet_group" "redis" {
  name       = "${local.app_env_name}-redis-subnets"
  subnet_ids = data.aws_subnets.subnets.ids
}

resource "aws_cloudwatch_log_group" "redis_log_group" {
  name              = "${local.app_env_name}-redis"
  retention_in_days = 90
}