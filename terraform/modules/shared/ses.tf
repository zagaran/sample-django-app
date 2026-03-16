# START_FEATURE ecs
resource "aws_ses_domain_identity" "ses_domain_identity" {
  domain = var.application_domain
}

# END_FEATURE ecs
