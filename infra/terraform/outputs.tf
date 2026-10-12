# ==============================================================================
# ATLAS Banking Copilot — Root Terraform Outputs (S21)
# ==============================================================================

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer (configure in Vercel backend URL)"
  value       = module.compute.alb_dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = module.compute.alb_arn
}

output "vpc_id" {
  description = "ID of the root VPC"
  value       = module.network.vpc_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = module.compute.ecs_cluster_name
}

output "ecs_service_name" {
  description = "Name of the ECS service running atlas-gateway"
  value       = module.compute.ecs_service_name
}

output "knowledge_bucket_name" {
  description = "Name of the S3 knowledge bucket"
  value       = module.data.s3_bucket_name
}

output "knowledge_bucket_arn" {
  description = "ARN of the S3 knowledge bucket"
  value       = module.data.s3_bucket_arn
}

output "opensearch_collection_endpoint" {
  description = "Endpoint of the OpenSearch Serverless collection"
  value       = module.data.opensearch_collection_endpoint
}

output "secrets_manager_secret_name" {
  description = "Name of the AWS Secrets Manager application secret"
  value       = module.security_iam.secrets_manager_secret_name
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.observability.log_group_name
}
