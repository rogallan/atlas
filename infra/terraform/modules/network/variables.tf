variable "environment" {
  type        = string
  description = "Target environment name (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project prefix for resource tagging and naming"
}

variable "vpc_cidr" {
  type        = string
  default     = "10.0.0.0/16"
  description = "CIDR block for the Virtual Private Cloud"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
  description = "CIDR blocks for public subnets (ALB, NAT Gateway)"
}

variable "private_subnet_cidrs" {
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
  description = "CIDR blocks for private subnets (ECS tasks, internal services)"
}

variable "availability_zones" {
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
  description = "AWS Availability Zones for multi-AZ deployment"
}

variable "single_nat_gateway" {
  type        = bool
  default     = true
  description = "If true, provision a single NAT Gateway to reduce development costs"
}
