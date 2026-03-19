terraform {
  required_providers {
    aws = { source="hashicorp/aws", version="~> 5.0" }
  }
}

provider "aws" { region="us-west-2" }

resource "aws_security_group" "sg" {
  name="web-sg"

  ingress { from_port=22 to_port=22 protocol="tcp" cidr_blocks=["0.0.0.0/0"] }
  ingress { from_port=80 to_port=80 protocol="tcp" cidr_blocks=["0.0.0.0/0"] }
}

resource "aws_s3_bucket" "s3" {
  bucket="assets-${random_id.suffix.hex}"
  acl="public-read"
}

resource "aws_db_instance" "db" {
  identifier="db-${random_id.suffix.hex}"
  engine="mysql"
  instance_class="db.t3.micro"
  allocated_storage=20
  storage_encrypted=true
  backup_retention_period=1
  username="admin"
  password=random_password.db.result
  publicly_accessible=false
  skip_final_snapshot=true
}

resource "aws_instance" "ec2" {
  ami="ami-0c55b159cbfafe1f0"
  instance_type="t2.micro"
  associate_public_ip_address=true
  vpc_security_group_ids=[aws_security_group.sg.id]

  root_block_device { encrypted=false volume_size=20 }
}

resource "aws_iam_role" "lambda_role" {
  name="lambda-${random_id.suffix.hex}"
  assume_role_policy=jsonencode({
    Version="2012-10-17"
    Statement=[{
      Action="sts:AssumeRole"
      Effect="Allow"
      Principal={Service="lambda.amazonaws.com"}
    }]
  })
}

resource "aws_lambda_function" "lambda" {
  filename="lambda_function_payload.zip"
  function_name="lambda-${random_id.suffix.hex}"
  role=aws_iam_role.lambda_role.arn
  handler="index.handler"
  runtime="nodejs18.x"
}

resource "aws_iam_role_policy" "policy" {
  name="policy-${random_id.suffix.hex}"
  role=aws_iam_role.lambda_role.id
  policy=jsonencode({
    Version="2012-10-17"
    Statement=[{
      Effect="Allow"
      Action=["logs:*","s3:*","dynamodb:*"]
      Resource="*"
    }]
  })
}

resource "aws_s3_bucket" "logs" {
  bucket="logs-${random_id.suffix.hex}"
  acl="private"

  server_side_encryption_configuration {
    rule { apply_server_side_encryption_by_default { sse_algorithm="AES256" } }
  }
}

resource "random_id" "suffix" { byte_length=4 }

resource "random_password" "db" {
  length=16
  special=false
}