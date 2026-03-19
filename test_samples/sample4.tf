resource "aws_s3_bucket" "no_versioning" {
  bucket="low-risk-no-versioning"
  acl="private"

  server_side_encryption_configuration {
    rule { apply_server_side_encryption_by_default { sse_algorithm="AES256" } }
  }
}

resource "aws_iam_policy" "policy" {
  name="low-risk-policy"
  policy=jsonencode({
    Version="2012-10-17"
    Statement=[{
      Action=["s3:GetObject","s3:PutObject","s3:ListBucket","s3:DeleteObject"]
      Effect="Allow"
      Resource="*"
    }]
  })
}

resource "aws_instance" "default" {
  ami="ami-0c55b159cbfafe1f0"
  instance_type="t2.micro"
}