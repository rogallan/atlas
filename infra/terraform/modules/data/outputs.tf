output "s3_bucket_name" {
  description = "Name of the knowledge corpus S3 bucket"
  value       = aws_s3_bucket.knowledge.id
}

output "s3_bucket_arn" {
  description = "ARN of the knowledge corpus S3 bucket"
  value       = aws_s3_bucket.knowledge.arn
}

output "opensearch_collection_id" {
  description = "ID of the OpenSearch Serverless vector collection"
  value       = aws_opensearchserverless_collection.vectors.id
}

output "opensearch_collection_arn" {
  description = "ARN of the OpenSearch Serverless vector collection"
  value       = aws_opensearchserverless_collection.vectors.arn
}

output "opensearch_collection_endpoint" {
  description = "Endpoint of the OpenSearch Serverless collection for vector queries"
  value       = aws_opensearchserverless_collection.vectors.collection_endpoint
}
