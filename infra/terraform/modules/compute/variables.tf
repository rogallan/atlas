variable "environment" {
  type        = string
  description = "Target environment name (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project prefix for resource tagging and naming"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where the ALB and ECS cluster reside"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "List of public subnet IDs for ALB placement"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs for ECS task placement"
}

variable "alb_security_group_id" {
  type        = string
  description = "Security group ID for ALB"
}

variable "ecs_security_group_id" {
  type        = string
  description = "Security group ID for ECS Fargate tasks"
}

variable "container_image" {
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.11-slim"
  description = "Container image URI for atlas-gateway"
}

variable "container_port" {
  type        = number
  default     = 8000
  description = "Port exposed by the FastAPI Gateway application container"
}

variable "cpu" {
  type        = number
  default     = 1024
  description = "Fargate CPU units (1024 = 1 vCPU)"
}

variable "memory" {
  type        = number
  default     = 2048
  description = "Fargate Memory allocation in MB"
}

variable "desired_count" {
  type        = number
  default     = 2
  description = "Desired number of running ECS task replicas"
}

variable "task_execution_role_arn" {
  type        = string
  description = "IAM role ARN allowing ECS to pull images and write logs"
}

variable "task_role_arn" {
  type        = string
  description = "IAM role ARN granting permissions to the running application code"
}

variable "cloudwatch_log_group_name" {
  type        = string
  description = "Name of the CloudWatch log group for container stdout/stderr"
}

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for logging and cloudwatch configuration"
}
