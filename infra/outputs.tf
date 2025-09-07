output "bucket_name" {
  value = aws_s3_bucket.scan_reports.bucket
}

output "iam_user" {
  value = aws_iam_user.jenkins_user.name
}

