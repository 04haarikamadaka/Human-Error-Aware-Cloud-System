# S3 bucket with public read access (HIGH severity)
resource "aws_s3_bucket" "public_bucket" {
  bucket = "my-public-bucket"
  acl    = "public-read"
  
  tags = {
    Name        = "Public bucket"
    Environment = "Test"
  }
}

# S3 bucket with public write access (CRITICAL severity)
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "my-insecure-bucket"
  acl    = "public-read-write"
}

# EC2 instance with public IP (HIGH severity)
resource "aws_instance" "web_server" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
  associate_public_ip_address = true
  
  tags = {
    Name = "Web Server"
  }
}

# EC2 instance without public IP (SECURE)
resource "aws_instance" "db_server" {
  ami           = "ami-123456"
  instance_type = "t2.micro"
  associate_public_ip_address = false
  
  tags = {
    Name = "Database Server"
  }
}