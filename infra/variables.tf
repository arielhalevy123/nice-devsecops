variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
  default     = "devsecops-scan-reports-ariel"
}

variable "region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "us-east-1"
}
