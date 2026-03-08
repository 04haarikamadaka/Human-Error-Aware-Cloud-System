# S3 bucket with public read (HIGH)
resource "aws_s3_bucket" "public_data" {
  bucket = "my-public-bucket"
  acl    = "public-read"
}

# S3 bucket with public write (CRITICAL)
resource "aws_s3_bucket" "public_write" {
  bucket = "my-public-write-bucket"
  acl    = "public-read-write"
}

# S3 bucket missing encryption (MEDIUM)
resource "aws_s3_bucket" "no_encryption" {
  bucket = "no-encryption-bucket"
  acl    = "private"
  # No encryption configuration
}

# EC2 with public IP (HIGH)
resource "aws_instance" "public_server" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
  associate_public_ip_address = true
}

# Security group with open SSH (CRITICAL)
resource "aws_security_group_rule" "ssh_from_world" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "sg-123456"
}

# Security group with open RDP (CRITICAL)
resource "aws_security_group_rule" "rdp_from_world" {
  type              = "ingress"
  from_port         = 3389
  to_port           = 3389
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "sg-123456"
}

# RDS publicly accessible (HIGH)
resource "aws_db_instance" "public_db" {
  identifier     = "public-db"
  engine         = "mysql"
  publicly_accessible = true
  storage_encrypted = false
}

# RDS with short backup retention (MEDIUM)
resource "aws_db_instance" "no_backup" {
  identifier     = "no-backup-db"
  engine         = "mysql"
  backup_retention_period = 1
}

# EBS volume unencrypted (HIGH)
resource "aws_ebs_volume" "data_volume" {
  availability_zone = "us-west-2a"
  size              = 40
  encrypted         = false
}