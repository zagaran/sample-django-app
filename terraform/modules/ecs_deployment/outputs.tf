output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.cluster.id
}

output "ecr_image_uri" {
  description = "The full URI of the ECR image"
  value = local.ecr_image_uri
}

output "ecr_repository_name" {
  description = "The name of the ECR repository"
  value = var.ecr_repository_name
}

output "public_ip" {
  description = "The public IP address of the load balancer for the web service"
  value       = aws_lb.alb.dns_name
}

output "web_service_name" {
  description = "The name of the ECS web service. This is also the container name."
  value = aws_ecs_service.web.name
}

output "web_network_configuration_security_groups" {
  description = "The security groups used by the ECS web task"
  value = aws_ecs_service.web.network_configuration[0].security_groups
}

output "web_network_configuration_subnets" {
  description = "The ID of the subnets used by the web task"
  value = aws_ecs_service.web.network_configuration[0].subnets
}

output "web_task_definition_arn" {
  description = "The ARN of the ECS web service task definition"
  value = aws_ecs_task_definition.web.arn
}