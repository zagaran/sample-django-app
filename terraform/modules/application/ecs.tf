# --------------------------------- Fargate ---------------------------------- #


resource "aws_ecs_cluster" "cluster" {
  name = "${local.app_env_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enhanced"
  }
}

resource "aws_ecs_cluster_capacity_providers" "fargate_provider" {
  cluster_name       = aws_ecs_cluster.cluster.name
  capacity_providers = ["FARGATE"]
}


# -------------------------------- Cloudwatch -------------------------------- #


resource "aws_cloudwatch_log_group" "web_log_group" {
  name              = "${local.app_env_name}-web"
  retention_in_days = 90
}

resource "aws_cloudwatch_log_group" "worker_log_group" {
  name              = "${local.app_env_name}-worker"
  retention_in_days = 90
}


# ----------------------------- Task Definitions ----------------------------- #


resource "aws_ecs_task_definition" "web" {
  family                   = "${local.app_env_name}-web"
  cpu                      = var.fargate_web_cpu
  memory                   = var.fargate_web_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  container_definitions = jsonencode([
    {
      name      = "${local.app_env_name}-web"
      image     = "${aws_ecr_repository.ecr.repository_url}:latest"
      secrets   = local.ecs_secrets
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
          awslogs-group         = aws_cloudwatch_log_group.web_log_group.name,
          awslogs-region        = data.aws_region.current.name,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.app_env_name}-worker"
  cpu                      = var.fargate_worker_cpu
  memory                   = var.fargate_worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  container_definitions = jsonencode([
    {
      name      = "${local.app_env_name}-worker"
      image     = "${aws_ecr_repository.ecr.repository_url}:latest"
      secrets   = local.ecs_secrets
      command   = local.ecs_worker_command
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
          awslogs-group         = aws_cloudwatch_log_group.worker_log_group.name,
          awslogs-region        = data.aws_region.current.name,
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}


# ------------------------------- ECS Services ------------------------------- #


resource "aws_ecs_service" "web" {
  name                   = "${local.app_env_name}-web"
  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.web.arn
  desired_count          = var.web_desired_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  load_balancer {
    target_group_arn = aws_lb_target_group.target_group.arn
    container_name   = "${local.app_env_name}-web"
    container_port   = 8080
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets = [
      aws_subnet.public_subnet_a.id,
      aws_subnet.public_subnet_b.id
    ]
    security_groups  = [aws_security_group.web.id]
    assign_public_ip = true
  }
}

resource "aws_ecs_service" "worker" {
  name                   = "${local.app_env_name}-worker"
  cluster                = aws_ecs_cluster.cluster.id
  task_definition        = aws_ecs_task_definition.worker.arn
  desired_count          = var.worker_desired_count
  launch_type            = "FARGATE"
  enable_execute_command = true

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  network_configuration {
    subnets = [
      aws_subnet.public_subnet_a.id,
      aws_subnet.public_subnet_b.id
    ]
    security_groups  = [aws_security_group.worker.id]
    assign_public_ip = true
  }
}