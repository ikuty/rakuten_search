output "gcs_bucket_name" {
  description = "Name of the created GCS bucket"
  value       = module.gcs.bucket_name
}

output "gcs_bucket_url" {
  description = "URL of the created GCS bucket"
  value       = module.gcs.bucket_url
}

output "service_account_email" {
  description = "Email address of the service account"
  value       = module.iam.service_account_email
}

output "service_account_key" {
  description = "Service account key in JSON format (base64 encoded)"
  value       = module.iam.service_account_key
  sensitive   = true
}
