resource "aws_iam_openid_connect_provider" "github_actions" {
  client_id_list = ["sts.amazonaws.com"]
  url = "https://token.actions.githubusercontent.com"
}

data "aws_iam_policy_document" "github_actions_assume_role_policy" {
  statement {
    effect = "Allow"
    principals {
      identifiers = [aws_iam_openid_connect_provider.github_actions.arn]
      type        = "Federated"
    }
    actions = ["sts:AssumeRoleWithWebIdentity"]
    condition {
      test     = "StringEquals"
      values = ["sts.amazonaws.com"]
      variable = "token.actions.githubusercontent.com:aud"
    }
    condition {
      test     = "StringLike"
      values = ["repo:${var.github_repo_owner_name}/${var.github_repo_name}:*"]
      variable = "token.actions.githubusercontent.com:sub"
    }
  }
}

resource "aws_iam_role" "github_actions_deployment_role" {
  name = var.role_name
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role_policy.json
}

data "aws_iam_policy_document" "github_actions_shared_access_policy" {
  statement {
    effect = "Allow"
    actions = [
      "s3:*"
    ]
    resources = [
      "arn:aws:s3:::mbta-edms-terraform-state",
      "arn:aws:s3:::mbta-edms-terraform-state/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "ec2:Describe*",
      "ec2:List*",
      "ecs:Describe*",
      "ecs:List*",
      "elasticache:Describe*",
      "elasticache:List*",
      "elasticloadbalancing:Describe*",
      "elasticloadbalancing:List*",
      "iam:Describe*",
      "iam:Get*",
      "iam:List*",
      "logs:Describe*",
      "logs:List*",
      "rds:Describe*",
      "rds:List*",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "github_actions_shared_access_policy" {
  name = "github-actions-shared-access-policy"
  role = aws_iam_role.github_actions_deployment_role.id
  policy = data.aws_iam_policy_document.github_actions_shared_access_policy.json
}
