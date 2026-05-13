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
      "arn:aws:ecr:*:*:repository/${var.ecr_repository_name}"
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
      # START_FEATURE celery
      "${aws_cloudwatch_log_group.worker_log_group.arn}:*",
      # END_FEATURE celery
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
      data.aws_secretsmanager_secret.web_config.arn
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
      "ses:GetSendQuota"
    ]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ses:SendBulkTemplatedEmail",
      "ses:SendEmail",
      "ses:SendRawEmail",
      "ses:SendTemplatedEmail"
    ]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "ses:FromAddress"
      values   = [var.ses_from_email]
    }
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
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "${local.app_env_name}-ecs-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_execution_role_policy" {
  name = "ecs-execution-role-policy"
  role = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.ecs_execution_role_policy.json
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${local.app_env_name}-ecs-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "ecs-task-role-policy"
  role = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.ecs_task_role_policy.json
}


# Github actions deployment policy -- conditional on role name being passed in
data "aws_iam_policy_document" "github_actions_deployment_policy" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:CompleteLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:InitiateLayerUpload",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:BatchGetImage",
      "ecr:Get*",
    ]
    resources = [local.ecr_repository_arn]
  }

  statement {
    effect = "Allow"
    actions = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecs:Get*",
      "ecs:RunTask",
      "ecs:UpdateService",
    ]
    resources = [
      local.ecs_arn_format,
      "${local.ecs_arn_format}/*",
      # START_FEATURE celery
      aws_ecs_task_definition.worker.arn,
      # END_FEATURE celery
      aws_ecs_task_definition.web.arn,
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:Describe*",
      "s3:Get*",
      "s3:List*",
    ]
    resources = [
      format("arn:aws:s3:::%s", aws_s3_bucket.bucket.id),
      format("arn:aws:s3:::%s/*", aws_s3_bucket.bucket.id),
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:Describe*",
      "secretsmanager:Get*",
    ]
    resources = [
      aws_secretsmanager_secret.web_infrastructure.arn,
      data.aws_secretsmanager_secret.web_config.arn,
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "iam:PassRole"
    ]
    resources = [
      aws_iam_role.ecs_execution_role.arn
    ]
  }
}

data "aws_iam_role" "github_actions_deployment_role" {
  count = var.github_actions_deployment_role_name == null ? 0 : 1
  name  = var.github_actions_deployment_role_name
}

resource "aws_iam_role_policy" "github_actions_deployment_policy" {
  count  = var.github_actions_deployment_role_name == null ? 0 : 1
  name   = "${local.app_env_name}-github-actions-deployment-policy"
  role   = data.aws_iam_role.github_actions_deployment_role[0].id
  policy = data.aws_iam_policy_document.github_actions_deployment_policy.json
}
