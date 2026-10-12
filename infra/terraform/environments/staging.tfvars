# Staging Environment Configuration
aws_region         = "us-east-1"
environment        = "staging"
project_name       = "atlas"
vpc_cidr           = "10.1.0.0/16"
single_nat_gateway = false
cpu                = 2048
memory             = 4096
desired_count      = 3
container_image    = "public.ecr.aws/docker/library/python:3.11-slim"
