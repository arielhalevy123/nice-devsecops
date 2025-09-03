output "bucket_name" {
  value = aws_s3_bucket.scan_reports.bucket
}

output "iam_user" {
  value = aws_iam_user.jenkins_user.name
}

output "access_key_id" {
  value = aws_iam_access_key.jenkins_key.id
  sensitive = true
}

output "secret_access_key" {
  value     = aws_iam_access_key.jenkins_key.secret
  sensitive = true
}