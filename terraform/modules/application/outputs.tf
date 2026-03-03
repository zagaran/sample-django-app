output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.cluster.id
}

output "ecr_image_uri" {
  description = "The full URI of the ECR image"
  value       = local.ecr_image_uri
}

output "ecr_repository_name" {
  description = "The name of the ECR repository"
  value       = aws_ecr_repository.ecr.name
}

output "web_service_name" {
  description = "The name of the ECS web service. This is also the container name."
  value       = aws_ecs_service.web.name
}

output "web_network_configuration_security_groups" {
  description = "The security groups used by the ECS web task"
  value       = aws_ecs_service.web.network_configuration[0].security_groups
}

output "web_network_configuration_subnets" {
  description = "The ID of one of the subnets used by the web task"
  value       = aws_ecs_service.web.network_configuration[0].subnets
}

output "web_task_definition_arn" {
  description = "The ARN of the ECS web service task definition"
  value       = aws_ecs_task_definition.web.arn
}

output "web_log_group_name" {
  description = "The name of the cloudwatch log group for the web service task"
  value       = aws_cloudwatch_log_group.web_log_group.name
}

output "worker_service_name" {
  description = "The name of the ECS worker service. This is also the container name."
  value       = aws_ecs_service.worker.name
}

output "worker_task_desired_count" {
  description = "The intended number of worker tasks"
  value       = aws_ecs_service.worker.desired_count
}

output "worker_log_group_name" {
  description = "The name of the cloudwatch log group for the worker service task"
  value       = aws_cloudwatch_log_group.worker_log_group.name
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.bucket.bucket
}