output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.app.arn
}

output "high_cpu_alarm_arn" {
  description = "ARN of the high CPU utilization alarm"
  value       = aws_cloudwatch_metric_alarm.high_cpu.arn
}
