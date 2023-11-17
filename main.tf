# Do not use. Old configuration.


terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region  = "us-east-1"
  profile = "rachelrj"
}

resource "aws_vpc" "cattleiq-scraper" {
}

resource "aws_subnet" "cattleiq-subnet-3" {
  vpc_id = aws_vpc.cattleiq-scraper.id
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "cattleiq-subnet-4" {
  vpc_id = aws_vpc.cattleiq-scraper.id
  cidr_block = "10.0.2.0/24"
}

resource "aws_security_group" "cattleiq_sg" {
  vpc_id = aws_vpc.cattleiq-scraper.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "cattleiq-sg"
  }
}

resource "aws_ecs_cluster" "cluster" {
  name = "cattleiq-ecs-cluster"
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = "ecs_execution_role"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_cloudwatch_log_group" "log_group" {
  name = "/ecs/cattleiq-ecs-service"
}

resource "aws_ecs_task_definition" "app_task" {
  family                   = "cattleiq-app-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = "arn:aws:iam::113365400202:role/ecs_execution_role"

  container_definitions = jsonencode([
    {
      name  = "cattleiq-app",
      image = "113365400202.dkr.ecr.us-east-1.amazonaws.com/cattleiq-scraper:cattle-iq-app-latest",
      portMappings = [
        {
          containerPort = 3000,
          hostPort      = 3000
        }
      ],
      environment = [
        {
          name  = "HUB_HOST",
          value = "selenium_hub"
        },
        {
          name  = "BROWSER",
          value = "firefox" 
        }
      ],
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.log_group.name,
          "awslogs-region"        = "us-east-1",
          "awslogs-stream-prefix" = "ecs-app"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app_service" {
  name            = "cattleiq-app-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.app_task.arn
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.cattleiq-subnet-3.id, aws_subnet.cattleiq-subnet-4.id]
    security_groups = [aws_security_group.cattleiq_sg.id]
  }
  
  desired_count = 1
  depends_on = [
    aws_ecs_task_definition.app_task
  ]
}

# VPC Endpoint for CloudWatch Logs
resource "aws_vpc_endpoint" "cloudwatch_logs_endpoint" {
  vpc_id             = aws_vpc.cattleiq-scraper.id
  service_name       = "com.amazonaws.us-east-1.logs"  # Adjusted to hardcoded value
  vpc_endpoint_type  = "Interface"
  security_group_ids = [aws_security_group.cattleiq_sg.id]
  subnet_ids         = [aws_subnet.cattleiq-subnet-3.id, aws_subnet.cattleiq-subnet-4.id]
  private_dns_enabled = true
}
