resource "aws_lb" "alb" {
  name               = "${local.app_env_name}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.load_balancer.id]
  subnets            = data.aws_subnets.subnets.ids
}


resource "aws_lb_target_group" "target_group" {
  name        = local.app_env_name
  port        = 8080
  protocol    = "HTTPS"
  vpc_id      = data.aws_vpc.vpc.id
  target_type = "ip"
  health_check {
    path = "/health-check/"
    protocol = "HTTPS"
  }
  lifecycle {
    create_before_destroy = false
  }
  stickiness {
    type = "lb_cookie"
    cookie_duration = 300
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = var.ssl_policy
  certificate_arn   = var.certificate_manager_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.target_group.arn
  }
}