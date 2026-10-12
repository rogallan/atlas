# ==============================================================================
# ATLAS Banking Copilot — Root Terraform Variables (S21)
# ==============================================================================

variable "aws_region" {
  type        = string
  default     = "us-east-1"
  description = "AWS region for all provisioned infrastructure"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Deployment environment name (dev, staging, prod)"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment variable must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project identifier prefix for naming resources"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the root VPC"
}

variable "container_image" {
  type        = string
  default     = "public.ecr.aws/docker/library/python:3.11-slim"
  description = "Container image URI for atlas-gateway in Amazon ECR"
}

variable "cpu" {
  type        = number
  default     = 1024
  description = "Fargate CPU units (1024 = 1 vCPU)"
}

variable "memory" {
  type        = number
  default     = 2048
  description = "Fargate memory allocation in MB (2048 = 2 GB)"
}

variable "desired_count" {
  type        = number
  default     = 2
  description = "Target replica count for ECS Fargate tasks"
}

variable "single_nat_gateway" {
  type        = bool
  default     = true
  description = "Whether to use a single NAT Gateway (recommended for dev to optimize costs)"
}
