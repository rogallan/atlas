# ==============================================================================
# ATLAS Banking Copilot — Data Module (S3 Knowledge Bucket & OpenSearch Serverless)
# ==============================================================================

# --- Regulatory Documents Knowledge S3 Bucket ---
resource "aws_s3_bucket" "knowledge" {
  bucket        = "${var.project_name}-${var.environment}-knowledge-corpus"
  force_destroy = var.force_destroy_bucket

  tags = {
    Name        = "${var.project_name}-${var.environment}-knowledge-corpus"
    Environment = var.environment
    Project     = var.project_name
    DataClass   = "Regulatory-Public-Norms"
  }
}

resource "aws_s3_bucket_versioning" "knowledge" {
  bucket = aws_s3_bucket.knowledge.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "knowledge" {
  bucket = aws_s3_bucket.knowledge.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "knowledge" {
  bucket = aws_s3_bucket.knowledge.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Amazon OpenSearch Serverless (Vector Search Collection) ---
resource "aws_opensearchserverless_security_policy" "encryption" {
  name        = "${var.project_name}-${var.environment}-enc"
  type        = "encryption"
  description = "Encryption at rest policy for OpenSearch Serverless vector collection"

  policy = jsonencode({
    Rules = [
      {
        ResourceType = "collection"
        Resource = [
          "collection/${var.project_name}-${var.environment}-vectors"
        ]
      }
    ],
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_collection" "vectors" {
  name        = "${var.project_name}-${var.environment}-vectors"
  type        = "VECTORSEARCH"
  description = "ATLAS Central Bank Vector Embeddings & Similarity Index"

  depends_on = [aws_opensearchserverless_security_policy.encryption]

  tags = {
    Name        = "${var.project_name}-${var.environment}-vectors"
    Environment = var.environment
  }
}
