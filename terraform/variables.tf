variable "aws_region" {
    type = string
    default = "us-east-1"
}

variable "ec2_instance_ami"{
    type = string
    default = "ami-0c02fb55956c7d316"
}

variable "ec2_instance_type" {
    type = string
    default = "t2.micro"
}