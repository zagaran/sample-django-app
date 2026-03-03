data "aws_route53_zone" "domain" {
  name = var.application_domain
}

resource "aws_route53_record" "ses_verification" {
  zone_id = data.aws_route53_zone.domain.zone_id
  name    = "_amazonses.${aws_ses_domain_identity.ses_domain_identity.domain}"
  type    = "TXT"
  ttl     = 600
  records = [aws_ses_domain_identity.ses_domain_identity.verification_token]
}
