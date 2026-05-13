output "github_actions_deployment_role_arn" {
  value = aws_iam_role.github_actions_deployment_role.arn
}

output "github_actions_deployment_role_name" {
  value = aws_iam_role.github_actions_deployment_role.name
}