# ==============================================================================
# ATLAS Banking Copilot — Root Terraform Composition (S21)
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "https://github.com/rogallan/atlas"
    }
  }
}

# --- 1. Network Tier ---
module "network" {
  source = "./modules/network"

  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  single_nat_gateway = var.single_nat_gateway
}

# --- 2. Data & Knowledge Tier ---
module "data" {
  source = "./modules/data"

  project_name         = var.project_name
  environment          = var.environment
  force_destroy_bucket = var.environment != "prod"
}

# --- 3. Security & IAM Tier ---
module "security_iam" {
  source = "./modules/security_iam"

  project_name              = var.project_name
  environment               = var.environment
  s3_bucket_arn             = module.data.s3_bucket_arn
  opensearch_collection_arn = module.data.opensearch_collection_arn
}

# --- 4. Compute Tier (ECS Fargate + ALB) ---
module "compute" {
  source = "./modules/compute"

  project_name              = var.project_name
  environment               = var.environment
  aws_region                = var.aws_region
  vpc_id                    = module.network.vpc_id
  public_subnet_ids         = module.network.public_subnet_ids
  private_subnet_ids        = module.network.private_subnet_ids
  alb_security_group_id     = module.network.alb_security_group_id
  ecs_security_group_id     = module.network.ecs_security_group_id
  task_execution_role_arn   = module.security_iam.task_execution_role_arn
  task_role_arn             = module.security_iam.task_role_arn
  cloudwatch_log_group_name = module.observability.log_group_name
  container_image           = var.container_image
  cpu                       = var.cpu
  memory                    = var.memory
  desired_count             = var.desired_count
}

# --- 5. Observability Tier (CloudWatch & Alarms) ---
module "observability" {
  source = "./modules/observability"

  project_name     = var.project_name
  environment      = var.environment
  ecs_cluster_name = module.compute.ecs_cluster_name
  ecs_service_name = module.compute.ecs_service_name
}
