provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "scan_reports" {
  bucket = var.bucket_name
  force_destroy = true

  tags = {
    Name        = "DevSecOps Scan Reports"
    Environment = "Dev"
  }
}

resource "aws_iam_user" "jenkins_user" {
  name = "jenkins-devsecops"
}

resource "aws_iam_policy" "s3_upload_policy" {
  name = "JenkinsS3UploadPolicy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Effect   = "Allow",
        Resource = [
          "arn:aws:s3:::${var.bucket_name}",
          "arn:aws:s3:::${var.bucket_name}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "attach_policy" {
  user       = aws_iam_user.jenkins_user.name
  policy_arn = aws_iam_policy.s3_upload_policy.arn
}

resource "aws_iam_access_key" "jenkins_key" {
  user = aws_iam_user.jenkins_user.name
}