# Random suffix for unique bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# KMS Key for encryption (optional, only if using KMS)
resource "aws_kms_key" "s3_key" {
  count = var.environment == "prod" ? 1 : 0
  
  description             = "KMS key for S3 bucket encryption in ${var.environment}"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  tags = local.common_tags
}

# S3 Bucket
resource "aws_s3_bucket" "web_assets" {
  bucket = "${local.name_prefix}-assets-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "prod"  # Allow deletion in non-prod

  tags = local.common_tags
}

# Block all public access (security best practice)
resource "aws_s3_bucket_public_access_block" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning (for data protection)
resource "aws_s3_bucket_versioning" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id
  
  versioning_configuration {
    status = var.environment == "prod" ? "Enabled" : "Suspended"
  }
}

# Server-side encryption configuration
resource "aws_s3_bucket_server_side_encryption_configuration" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id

  rule {
    apply_server_side_encryption_by_default {
      # Use KMS for production, AES256 for other environments
      sse_algorithm     = var.environment == "prod" ? "aws:kms" : "AES256"
      kms_master_key_id = var.environment == "prod" ? aws_kms_key.s3_key[0].arn : null
    }
    bucket_key_enabled = true  # Reduce KMS costs by using bucket keys
  }
}

# Enable lifecycle rules (cost optimization)
resource "aws_s3_bucket_lifecycle_configuration" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id

  rule {
    id     = "old_versions"
    status = "Enabled"

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "expire_old_logs"
    status = var.environment == "prod" ? "Enabled" : "Disabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = 90
    }
  }
}

# Bucket policy to enforce HTTPS (security best practice)
resource "aws_s3_bucket_policy" "web_assets" {
  bucket = aws_s3_bucket.web_assets.id
  policy = data.aws_iam_policy_document.bucket_policy.json
}

data "aws_iam_policy_document" "bucket_policy" {
  statement {
    sid = "DenyInsecureConnections"
    effect = "Deny"
    principals {
      type        = "*"
      identifiers = ["*"]
    }
    actions = ["s3:*"]
    resources = [
      aws_s3_bucket.web_assets.arn,
      "${aws_s3_bucket.web_assets.arn}/*"
    ]
    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

# Logging bucket (for audit purposes)
resource "aws_s3_bucket" "access_logs" {
  count = var.environment == "prod" ? 1 : 0
  
  bucket = "${local.name_prefix}-access-logs-${random_id.bucket_suffix.hex}"
  force_destroy = false

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-access-logs"
  })
}

# Enable logging for main bucket
resource "aws_s3_bucket_logging" "web_assets" {
  count = var.environment == "prod" ? 1 : 0
  
  bucket = aws_s3_bucket.web_assets.id

  target_bucket = aws_s3_bucket.access_logs[0].id
  target_prefix = "log/"
}

# Variable for encryption type
variable "s3_encryption_type" {
  description = "Type of encryption for S3 bucket (AES256 or KMS)"
  type        = string
  default     = "AES256"
  
  validation {
    condition     = contains(["AES256", "KMS"], var.s3_encryption_type)
    error_message = "Encryption type must be either AES256 or KMS."
  }
}

# Outputs
output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.web_assets.arn
}

output "bucket_encryption" {
  description = "Encryption status of the bucket"
  value       = aws_s3_bucket_server_side_encryption_configuration.web_assets.rule[0].apply_server_side_encryption_by_default[0].sse_algorithm
}