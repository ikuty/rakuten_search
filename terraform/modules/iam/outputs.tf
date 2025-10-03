output "service_account_email" {
  description = "Email address of the service account"
  value       = google_service_account.service_account.email
}

output "service_account_name" {
  description = "Name of the service account"
  value       = google_service_account.service_account.name
}

output "service_account_id" {
  description = "ID of the service account"
  value       = google_service_account.service_account.account_id
}

output "service_account_key" {
  description = "Service account key in JSON format (sensitive)"
  value       = var.create_key ? google_service_account_key.service_account_key[0].private_key : null
  sensitive   = true
}
