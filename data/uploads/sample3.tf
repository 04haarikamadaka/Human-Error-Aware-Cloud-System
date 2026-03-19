resource "aws_s3_bucket" "no_encryption" {
  bucket="medium-risk-no-encryption"
  acl="private"
}

resource "aws_db_instance" "rds" {
  identifier="medium-risk-db"
  engine="postgres"
  instance_class="db.t3.micro"
  backup_retention_period=1
  storage_encrypted=true
  publicly_accessible=false
}

resource "aws_lambda_function" "lambda" {
  filename="lambda_function_payload.zip"
  function_name="medium-risk-lambda"
  role=aws_iam_role.lambda_role.arn
  handler="index.test"
  runtime="nodejs18.x"
}

resource "aws_elasticache_cluster" "cache" {
  cluster_id="medium-risk-cache"
  engine="redis"
  node_type="cache.t3.micro"
  num_cache_nodes=1
  at_rest_encryption_enabled=false
}

# IAM password policy intentionally missing