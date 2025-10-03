# GCP Project Configuration
project_id = "ikutycom"
region     = "asia-northeast1"

# GCS Bucket Configuration
bucket_name        = "rakuten-kimono"
gcs_location       = "asia-northeast1"
gcs_force_destroy  = true
gcs_versioning_enabled = false

# Lifecycle rules: Delete files older than 90 days
gcs_lifecycle_rules = [
  {
    action = {
      type = "Delete"
    }
    condition = {
      age = 90
    }
  }
]

# Service Account Configuration
service_account_id           = "rakuten-kimono-terraform"
service_account_display_name = "rakuten-kimono-terraform Service Account"
service_account_project_roles = []
create_service_account_key   = true

# Common Labels
common_labels = {
  project     = "rakuten-search"
  environment = "dev"
}
