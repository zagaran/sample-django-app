resource "aws_security_group" "web" {
  name   = "${local.app_env_name}-web"
  vpc_id = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.load_balancer.id]
  }

  tags = {
    Name = "${var.application_name} ${var.environment} web"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "worker" {
  name   = "${local.app_env_name}-worker"
  vpc_id = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.application_name} ${var.environment} worker"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "tasks" {
  name   = "${local.app_env_name}-tasks"
  vpc_id = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.application_name} ${var.environment} tasks"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "database" {
  name   = "${local.app_env_name}-db"
  vpc_id = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 5432
    to_port   = 5432
    protocol  = "tcp"
    security_groups = [
      aws_security_group.web.id,
      aws_security_group.worker.id,
    ]
  }

  tags = {
    Name = "${var.application_name} ${var.environment} database"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "redis" {
  name   = "${local.app_env_name}-redis"
  vpc_id = aws_vpc.vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 6379
    to_port   = 6379
    protocol  = "tcp"
    security_groups = [
      aws_security_group.web.id,
      aws_security_group.worker.id,
    ]
  }

  tags = {
    Name = "${var.application_name} ${var.environment} redis"
  }

  lifecycle {
    create_before_destroy = true
  }
}