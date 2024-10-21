resource "aws_ecs_cluster" "cluster" {
  name = format("%-cluster", var.environment_name)

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}


resource "aws_ecs_cluster_capacity_providers" "fargate_provider" {
  cluster_name = aws_ecs_cluster.cluster.name

  capacity_providers = ["FARGATE"]
}


locals {
  ecs_secrets = [
    {
      name : "DATABASE_URL",
      valueFrom : "${aws_secretsmanager_secret.web_infrastructure.arn}:DATABASE_URL::"
    },
    {
      name : "SECRET_KEY",
      valueFrom : "${aws_secretsmanager_secret.web_infrastructure.arn}:SECRET_KEY::"
    },
    {
      name : "AWS_STORAGE_BUCKET_NAME",
      valueFrom : "${aws_secretsmanager_secret.web_infrastructure.arn}:AWS_STORAGE_BUCKET_NAME::"
    },
    {
      name : "DEFAULT_FROM_EMAIL",
      valueFrom : "${aws_secretsmanager_secret.web_infrastructure.arn}:DEFAULT_FROM_EMAIL::"
    },
  ]
}


resource "aws_ecs_task_definition" "web" {
  family = "${var.environment_name}-web"
  
  container_definitions = jsonencode([
    {
      name      = "${var.environment_name}-web"
      image     = var.ecr_image_uri
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
            awslogs-group = aws_cloudwatch_log_group.log_group.name,
            awslogs-region = data.aws_region.current.name,
            awslogs-stream-prefix = "ecs"
        }
      }
      secrets = local.ecs_secrets
    }
  ])

  requires_compatibilities = ["FARGATE"]
  cpu       = var.container_web_cpu
  memory    = var.container_web_memory
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  network_mode = "awsvpc"
  task_role_arn = aws_iam_role.ecs_task_role.arn
}


resource "aws_ecs_service" "web" {
  name                   = "${var.environment_name}-web"
  cluster                = aws_ecs_cluster.application.id
  task_definition        = aws_ecs_task_definition.web.arn
  desired_count          = var.container_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.application.arn
    container_name   = "${local.app_env_name}-web"
    container_port   = 8080
  }

  network_configuration {
    subnets          = data.aws_subnets.subnets.ids
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = true
  }
}


resource "aws_cloudwatch_log_group" "log_group" {
  name              = var.environment_name
  retention_in_days = 90
}