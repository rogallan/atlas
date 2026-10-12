output "ecs_cluster_id" {
  description = "ID of the provisioned ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the provisioned ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.main.arn
}

output "target_group_arn" {
  description = "ARN of the ALB target group routing to the gateway"
  value       = aws_lb_target_group.gateway.arn
}

output "ecs_service_name" {
  description = "Name of the provisioned ECS Fargate service"
  value       = aws_ecs_service.gateway.name
}
