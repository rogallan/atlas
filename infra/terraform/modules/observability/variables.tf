variable "environment" {
  type        = string
  description = "Target environment name (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project prefix for resource tagging and naming"
}

variable "log_retention_days" {
  type        = number
  default     = 30
  description = "Retention period in days for CloudWatch application logs"
}

variable "ecs_cluster_name" {
  type        = string
  description = "Name of the ECS cluster to monitor with metric alarms"
}

variable "ecs_service_name" {
  type        = string
  description = "Name of the ECS service to monitor with metric alarms"
}
