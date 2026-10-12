variable "environment" {
  type        = string
  description = "Target environment name (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project prefix for resource tagging and naming"
}

variable "force_destroy_bucket" {
  type        = bool
  default     = true
  description = "Whether to allow force deletion of the knowledge S3 bucket in non-prod"
}
