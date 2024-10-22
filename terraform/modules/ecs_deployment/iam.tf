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
      "arn:aws:logs:*:*:log-group:${var.environment_name}:*",
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      "arn:aws:secretsmanager:*:*:secret:${aws_secretsmanager_secret.web_infrastructure.name}-*",
      "arn:aws:secretsmanager:*:*:secret:${data.aws_secretsmanager_secret.web_config.name}-*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "kms:Decrypt"
    ]
    resources = [
      format("arn:aws:kms:*:*:aws/secretsmanager")
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
      "ses:SendEmail",
      "ses:SendRawEmail",
      "ses:GetSendQuota"
    ]
    resources = [
      format("arn:aws:ses:*:*:identity/%s", var.ses_identity)
    ]
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
      format("arn:aws:kms:*:*:aws/secretsmanager")
    ]
  }
}

resource "aws_iam_role" "ecs_execution_role" {
  name = format("%s-ecs-execution-role", var.environment_name)
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_execution_role_policy" {
  name = "ecs-execution-role-policy"
  role = aws_iam_role.ecs_execution_role.id
  policy = data.aws_iam_policy_document.ecs_execution_role_policy.json
}

resource "aws_iam_role" "ecs_task_role" {
  name = format("%s-ecs-task-role", var.environment_name)
  assume_role_policy = data.aws_iam_policy_document.ecs_assume_role_policy.json
}

resource "aws_iam_role_policy" "ecs_task_role_policy" {
  name = "ecs-task-role-policy"
  role = aws_iam_role.ecs_task_role.id
  policy = data.aws_iam_policy_document.ecs_task_role_policy.json
}
