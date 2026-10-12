# ==============================================================================
# ATLAS Banking Copilot — Observability Module (CloudWatch Logs & Metric Alarms)
# ==============================================================================

# --- CloudWatch Log Group ---
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project_name}-${var.environment}-gateway"
  retention_in_days = var.log_retention_days

  tags = {
    Name        = "${var.project_name}-${var.environment}-log-group"
    Environment = var.environment
  }
}

# --- CloudWatch Metric Alarm: High CPU Utilization (> 85% for 2 periods) ---
resource "aws_cloudwatch_metric_alarm" "high_cpu" {
  alarm_name          = "${var.project_name}-${var.environment}-high-cpu-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Triggers when ECS cluster CPU exceeds 85% sustained utilization"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-high-cpu"
    Environment = var.environment
  }
}

# --- CloudWatch Metric Alarm: High Memory Utilization (> 85% for 2 periods) ---
resource "aws_cloudwatch_metric_alarm" "high_memory" {
  alarm_name          = "${var.project_name}-${var.environment}-high-memory-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Triggers when ECS cluster memory exceeds 85% sustained utilization"

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-high-memory"
    Environment = var.environment
  }
}
