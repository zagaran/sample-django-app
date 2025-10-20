data "aws_ses_domain_identity" "ses_domain_identity" {
  domain = var.data_email_domain
}

data "aws_iam_policy_document" "ses_domain_identity_policy" {

  statement {
    actions = [
      "ses:*"
    ]
    resources = [
      data.aws_ses_domain_identity.ses_domain_identity.arn
    ]
    principals {
      type = "AWS"
      identifiers = [
        aws_iam_role.ecs_task_role.arn
      ]
    }
  }
}

resource "aws_ses_identity_policy" "allow_ecs" {
  identity = data.aws_ses_domain_identity.ses_domain_identity.arn
  policy   = data.aws_iam_policy_document.ses_domain_identity_policy.json
  name     = "${local.app_env_name}-Allow-ECS"
}