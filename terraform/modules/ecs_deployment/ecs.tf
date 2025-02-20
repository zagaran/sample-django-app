resource "aws_ecs_cluster" "cluster" {
  name = "${local.app_env_name}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "fargate_provider" {
  cluster_name = aws_ecs_cluster.cluster.name

  capacity_providers = ["FARGATE"]
}

resource "aws_ecs_task_definition" "web" {
  family = "${local.app_env_name}-web"
  
  container_definitions = jsonencode([
    {
      name      = "${local.app_env_name}-web"
      image     = local.ecr_image_uri
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
            awslogs-group = aws_cloudwatch_log_group.web_log_group.name,
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
  name                   = "${local.app_env_name}-web"
  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.web.arn
  desired_count          = var.container_web_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = "${local.app_env_name}-web"
    container_port   = 8080
  }

  network_configuration {
    subnets          = data.aws_subnets.subnets.ids
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = true
  }
}

resource "aws_cloudwatch_log_group" "web_log_group" {
  name              = "${local.app_env_name}-web"
  retention_in_days = 90
}


resource "aws_ecs_task_definition" "worker" {
  family = "${local.app_env_name}-worker"

  container_definitions = jsonencode([
    {
      name      = "${local.app_env_name}-worker"
      image     = local.ecr_image_uri
      essential = true
      logConfiguration = {
        logDriver = "awslogs",
        options = {
            awslogs-group = aws_cloudwatch_log_group.worker_log_group.name,
            awslogs-region = data.aws_region.current.name,
            awslogs-stream-prefix = "ecs"
        }
      }
      secrets = local.ecs_secrets
      command = local.ecs_worker_command
    }
  ])

  requires_compatibilities = ["FARGATE"]
  cpu       = var.container_worker_cpu
  memory    = var.container_worker_memory
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  network_mode = "awsvpc"
  task_role_arn = aws_iam_role.ecs_task_role.arn
}

resource "aws_ecs_service" "worker" {
  name = "${local.app_env_name}-worker"

  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.worker.arn
  desired_count          = var.container_worker_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets          = data.aws_subnets.subnets.ids
    security_groups  = [aws_security_group.worker.id]
    assign_public_ip = false
  }
}

resource "aws_cloudwatch_log_group" "worker_log_group" {
  name              = "${local.app_env_name}-worker"
  retention_in_days = 90
}