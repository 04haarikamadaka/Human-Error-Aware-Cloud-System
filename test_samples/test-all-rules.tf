# comprehensive_test_all_rules.tf

terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" { region = "us-west-2" }

# ----------- S3 -----------
resource "aws_s3_bucket" "public_read" {
  bucket = "test-pr-${random_id.suffix.hex}"
  acl    = "public-read"
}

resource "aws_s3_bucket" "public_write" {
  bucket = "test-pw-${random_id.suffix.hex}"
  acl    = "public-read-write"
}

resource "aws_s3_bucket" "no_encryption" {
  bucket = "test-ne-${random_id.suffix.hex}"
}

resource "aws_s3_bucket" "no_versioning" {
  bucket = "test-nv-${random_id.suffix.hex}"
  server_side_encryption_configuration {
    rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
  }
}

# ----------- EC2 -----------
resource "aws_security_group" "sg" { name = "test-sg-${random_id.suffix.hex}" }

resource "aws_security_group_rule" "ssh" {
  type="ingress" from_port=22 to_port=22 protocol="tcp"
  cidr_blocks=["0.0.0.0/0"] security_group_id=aws_security_group.sg.id
}

resource "aws_security_group_rule" "rdp" {
  type="ingress" from_port=3389 to_port=3389 protocol="tcp"
  cidr_blocks=["0.0.0.0/0"] security_group_id=aws_security_group.sg.id
}

resource "aws_instance" "ec2" {
  ami="ami-0c55b159cbfafe1f0" instance_type="t2.micro"
  associate_public_ip_address=true
  vpc_security_group_ids=[aws_security_group.sg.id]
  root_block_device { encrypted=true volume_size=20 }
}

# ----------- RDS -----------
resource "aws_db_instance" "public" {
  identifier="rds-p-${random_id.suffix.hex}"
  engine="mysql" instance_class="db.t3.micro"
  allocated_storage=20 storage_encrypted=true
  publicly_accessible=true
  username="admin" password=random_password.db.result
  skip_final_snapshot=true
}

resource "aws_db_instance" "unencrypted" {
  identifier="rds-u-${random_id.suffix.hex}"
  engine="postgres" instance_class="db.t3.micro"
  allocated_storage=20 storage_encrypted=false
  publicly_accessible=false
  username="admin" password=random_password.db.result
  skip_final_snapshot=true
}

resource "aws_db_instance" "short_backup" {
  identifier="rds-b-${random_id.suffix.hex}"
  engine="mysql" instance_class="db.t3.micro"
  allocated_storage=20 storage_encrypted=true
  backup_retention_period=1
  username="admin" password=random_password.db.result
  skip_final_snapshot=true
}

# ----------- IAM -----------
resource "aws_iam_access_key" "root" { user = "root" }

resource "aws_iam_user" "user" { name = "test-${random_id.suffix.hex}" }

resource "aws_iam_policy" "wildcard" {
  name = "policy-${random_id.suffix.hex}"
  policy = jsonencode({
    Version="2012-10-17"
    Statement=[{
      Action=["s3:*","ec2:*","iam:*"]
      Effect="Allow"
      Resource="*"
    }]
  })
}

# ----------- EBS -----------
resource "aws_ebs_volume" "ebs" {
  availability_zone="us-west-2a"
  size=40
  encrypted=false
}

# ----------- CloudFront -----------
resource "aws_cloudfront_distribution" "cf" {
  origin {
    domain_name = aws_s3_bucket.public_read.bucket_regional_domain_name
    origin_id   = "S3"
  }
  enabled = true
  default_cache_behavior {
    allowed_methods=["GET","HEAD"]
    cached_methods=["GET","HEAD"]
    target_origin_id="S3"
    viewer_protocol_policy="allow-all"
    forwarded_values {
      query_string=false
      cookies { forward="none" }
    }
  }
  restrictions { geo_restriction { restriction_type="none" } }
  viewer_certificate { cloudfront_default_certificate=true }
}

# ----------- Lambda -----------
resource "aws_iam_role" "lambda_role" {
  name="lambda-role-${random_id.suffix.hex}"
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
  handler="index.test"
  runtime="nodejs18.x"
}

# ----------- ElastiCache -----------
resource "aws_elasticache_cluster" "cache" {
  cluster_id="cache-${random_id.suffix.hex}"
  engine="redis"
  node_type="cache.t3.micro"
  num_cache_nodes=1
  at_rest_encryption_enabled=false
  transit_encryption_enabled=false
}

# ----------- Network + SG -----------
resource "aws_vpc" "vpc" { cidr_block="10.0.0.0/16" }

resource "aws_default_security_group" "default" {
  vpc_id = aws_vpc.vpc.id
  ingress { protocol=-1 self=true from_port=0 to_port=0 }
  egress  { protocol="-1" cidr_blocks=["0.0.0.0/0"] from_port=0 to_port=0 }
}

# ----------- Secrets -----------
variable "db_password" {
  default = "SuperSecretPassword123!"
}

# ----------- Helpers -----------
resource "random_id" "suffix" { byte_length = 4 }

resource "random_password" "db" {
  length = 16
  special = false
}