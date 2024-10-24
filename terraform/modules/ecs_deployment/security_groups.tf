resource "aws_security_group" "load_balancer" {
  name = format("%s %s load balancer", var.application_name, var.environment_name)
  
  ingress {
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  ingress {
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = format("%s-%s-lb", var.application_name, var.environment_name)
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "web" {
  name = format("%s %s web", var.application_name, var.environment_name)

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.load_balancer.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = format("%s-%s-web", var.application_name, var.environment_name)
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_security_group" "database" {
  name = format("%s %s database", var.application_name, var.environment_name)

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = format("%s-%s-db", var.application_name, var.environment_name)
  }
  
  lifecycle {
    create_before_destroy = true
  }
}
