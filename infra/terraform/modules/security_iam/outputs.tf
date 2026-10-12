output "task_execution_role_arn" {
  description = "ARN of the ECS task execution role"
  value       = aws_iam_role.task_execution.arn
}

output "task_role_arn" {
  description = "ARN of the ECS application task role"
  value       = aws_iam_role.task.arn
}

output "secrets_manager_secret_arn" {
  description = "ARN of the Secrets Manager application secret"
  value       = aws_secretsmanager_secret.app.arn
}

output "secrets_manager_secret_name" {
  description = "Name of the Secrets Manager application secret"
  value       = aws_secretsmanager_secret.app.name
}
