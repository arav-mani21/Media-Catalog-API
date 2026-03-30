terraform {
    required_providers{
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = var.aws_region
}

resource "aws_dynamodb_table" "books_table" {
    name = "books"
    billing_mode = "PAY_PER_REQUEST"

    hash_key = "id"

    attribute {
        name = "id"
        type = "S"
    }

    point_in_time_recovery {
        enabled = true
    }
}

resource "aws_dynamodb_table" "movies_table" {
    name = "movies"
    billing_mode = "PAY_PER_REQUEST"

    hash_key = "id"

    attribute {
        name = "id"
        type = "S"
    }

    point_in_time_recovery {
        enabled = true
    }
}

resource "aws_key_pair" "fastapi_server_key" {
    key_name = "fastapi-ec2-key"
    public_key = file("~/.ssh/id_rsa_ec2.pub")
}

resource "aws_security_group" "fastapi_server_sg"{
    name = "fastapi-ec2-sg"
    description = "Allow SSH inbound"

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 8001
        to_port     = 8001
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_instance" "fastapi_server" {
    ami = var.ec2_instance_ami
    instance_type = var.ec2_instance_type
    key_name = aws_key_pair.fastapi_server_key.key_name
    vpc_security_group_ids = [aws_security_group.fastapi_server_sg.id]

    tags = {
        Name = "fastapi-ec2"
    }

    user_data = file("${path.module}/../user_data.sh")
}

resource "aws_iam_role" "ec2_role_dynamodb" {
    name = "fastapi-ec2-dynamodb-role"
    description = "Allows FastAPI EC2 instance to access DynamoDB tables Books and Movies"

    assume_role_policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "ec2.amazonaws.com"
                }
            }
        ]
    })
}

resource "aws_iam_policy" "dynamodb_access" {
    name = "fastapi-ec2-dynamodb-access"

    policy = jsonencode({
        Version = "2012-10-17",
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem"
                ]
                Resource = [
                    aws_dynamodb_table.books_table.arn,
                    aws_dynamodb_table.movies_table.arn
                ]
            }
        ]
    })
}

resource "aws_iam_role_policy_attachment" "attach" {
    role = aws_iam_role.ec2_role_dynamodb.name
    policy_arn = aws_iam_policy.dynamodb_access.arn
}