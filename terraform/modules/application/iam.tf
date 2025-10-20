data "aws_iam_policy_document" "ecs_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "ecs_execution_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:GetAuthorizationToken"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage"
    ]
    resources = [
      "arn:aws:ecr:*:*:repository/${aws_ecr_repository.ecr.name}",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.web_log_group.arn}:*",
      "${aws_cloudwatch_log_group.worker_log_group.arn}:*",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      aws_secretsmanager_secret.web_infrastructure.arn,
      aws_secretsmanager_secret.web_config.arn,
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      "arn:aws:kms:*:*:aws/secretsmanager"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:DescribeServices"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "autoscaling:*"
    ]
    resources = ["*"]
  }
}

data "aws_iam_policy_document" "ecs_task_role_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      format("arn:aws:s3:::%s", aws_s3_bucket.bucket.id),
      format("arn:aws:s3:::%s/*", aws_s3_bucket.bucket.id)
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      "arn:aws:kms:*:*:aws/secretsmanager"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ses:*"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecs:RunTask",
      "ecs:DescribeServices",
      "ecs:StopTask",
      "ecs:DescribeTasks",
      "iam:GetRole",
      "iam:PassRole"
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role" "ecs_execution_role" {
  name               = "${local.app_env_name}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_execution_role_policy" {
  name   = "ecs-execution-role-policy"
  role   = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.ecs_execution_role_policy.json
}

resource "aws_iam_role" "ecs_task_role" {
  name               = "${local.app_env_name}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name   = "ecs-task-role-policy"
  role   = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.ecs_task_role_policy.json
}

# ------------------------------ Github Actions ------------------------------ #


data "aws_iam_openid_connect_provider" "github" {
  count = local.enable_github_oidc ? 1 : 0
  arn   = var.github_oidc_provider_arn
}

resource "aws_iam_role" "github_actions_deployment_role" {
  count = local.enable_github_oidc ? 1 : 0
  name  = "${local.app_env_name}-github-actions-deployment-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Federated = data.aws_iam_openid_connect_provider.github[0].arn
        },
        Action = "sts:AssumeRoleWithWebIdentity",
        Condition = {
          StringEquals = {
            "token.actions.githubusercontent.com:aud" = "sts.amazonaws.com"
          },
          StringLike = {
            "token.actions.githubusercontent.com:sub" = [
              "repo:${var.remote_repo_name}:*"
            ]
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "github_actions_admin_access" {
  count      = local.enable_github_oidc ? 1 : 0
  role       = "${local.app_env_name}-github-actions-deployment-role"
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}