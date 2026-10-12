# ==============================================================================
# ATLAS Banking Copilot — Security & IAM Module (Least-Privilege Roles & Secrets)
# ==============================================================================

# --- Secrets Manager ---
resource "aws_secretsmanager_secret" "app" {
  name                    = "${var.project_name}-${var.environment}-secrets"
  description             = "Runtime API keys and configuration secrets for ATLAS Copilot"
  recovery_window_in_days = 0

  tags = {
    Name        = "${var.project_name}-${var.environment}-secrets"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "app" {
  secret_id = aws_secretsmanager_secret.app.id
  secret_string = jsonencode({
    ENVIRONMENT  = var.environment
    DATABASE_URL = "sqlite:////app/data/atlas.db"
    API_KEY      = "atlas-dev-key-placeholder"
  })
}

# --- ECS Task Execution Role (Pulling images, writing logs, reading secrets) ---
resource "aws_iam_role" "task_execution" {
  name = "${var.project_name}-${var.environment}-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-task-execution-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "task_execution_managed" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_policy" "task_execution_secrets" {
  name        = "${var.project_name}-${var.environment}-task-exec-secrets-policy"
  description = "Allows ECS agent to read Secrets Manager values during container start"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [aws_secretsmanager_secret.app.arn]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution_secrets" {
  role       = aws_iam_role.task_execution.name
  policy_arn = aws_iam_policy.task_execution_secrets.arn
}

# --- ECS Task Role (Permissions for application code at runtime) ---
resource "aws_iam_role" "task" {
  name = "${var.project_name}-${var.environment}-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-task-role"
    Environment = var.environment
  }
}

resource "aws_iam_policy" "task_app_permissions" {
  name        = "${var.project_name}-${var.environment}-task-app-policy"
  description = "Least privilege runtime access for ATLAS Banking Copilot application"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Read regulatory PDFs from S3
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          var.s3_bucket_arn,
          "${var.s3_bucket_arn}/*"
        ]
      },
      # OpenSearch Serverless Vector query permissions
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll"
        ]
        Resource = [var.opensearch_collection_arn]
      },
      # AWS X-Ray Tracing emission
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_app_permissions" {
  role       = aws_iam_role.task.name
  policy_arn = aws_iam_policy.task_app_permissions.arn
}
