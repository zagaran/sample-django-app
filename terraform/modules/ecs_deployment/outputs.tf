output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.cluster.id
}

output "public_ip" {
  description = "The public IP address of the load balancer for the web service"
  value       = aws_lb.alb.dns_name
}