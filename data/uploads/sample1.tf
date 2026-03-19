resource "aws_iam_access_key" "root" { user = "root" }

resource "aws_security_group_rule" "ssh" {
  type="ingress" from_port=22 to_port=22 protocol="tcp"
  cidr_blocks=["0.0.0.0/0"] security_group_id=aws_security_group.web.id
}

resource "aws_security_group_rule" "rdp" {
  type="ingress" from_port=3389 to_port=3389 protocol="tcp"
  cidr_blocks=["0.0.0.0/0"] security_group_id=aws_security_group.windows.id
}

resource "aws_s3_bucket" "public_write" {
  bucket="critical-public-write-bucket"
  acl="public-read-write"
}

variable "aws_access_key" { default="AKIAIOSFODNN7EXAMPLE" }
variable "aws_secret_key" { default="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" }