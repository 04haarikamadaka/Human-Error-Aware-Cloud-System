resource "aws_s3_bucket" "public_read" {
  bucket="high-risk-public-bucket"
  acl="public-read"
}

resource "aws_instance" "ec2" {
  ami="ami-0c55b159cbfafe1f0"
  instance_type="t2.micro"
  associate_public_ip_address=true
}

resource "aws_db_instance" "rds" {
  identifier="high-risk-db"
  engine="mysql"
  instance_class="db.t3.micro"
  publicly_accessible=true
  storage_encrypted=false
  username="admin"
  password="Password123!"
}

resource "aws_ebs_volume" "ebs" {
  availability_zone="us-west-2a"
  size=40
  encrypted=false
}

# CloudTrail intentionally missing