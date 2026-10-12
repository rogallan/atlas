# Development Environment Configuration
aws_region         = "us-east-1"
environment        = "dev"
project_name       = "atlas"
vpc_cidr           = "10.0.0.0/16"
single_nat_gateway = true
cpu                = 1024
memory             = 2048
desired_count      = 2
container_image    = "public.ecr.aws/docker/library/python:3.11-slim"
