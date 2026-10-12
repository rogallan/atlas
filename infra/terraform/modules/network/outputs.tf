output "vpc_id" {
  description = "The ID of the provisioned Virtual Private Cloud"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets for ALB placement"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets for ECS tasks placement"
  value       = aws_subnet.private[*].id
}

output "alb_security_group_id" {
  description = "Security group ID attached to the Application Load Balancer"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "Security group ID attached to the ECS Fargate tasks"
  value       = aws_security_group.ecs.id
}
