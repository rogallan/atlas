variable "environment" {
  type        = string
  description = "Target environment name (dev, staging, prod)"
}

variable "project_name" {
  type        = string
  default     = "atlas"
  description = "Project prefix for resource tagging and naming"
}

variable "s3_bucket_arn" {
  type        = string
  description = "ARN of the knowledge corpus S3 bucket for task role least-privilege access"
}

variable "opensearch_collection_arn" {
  type        = string
  description = "ARN of the OpenSearch Serverless collection for vector queries"
}
