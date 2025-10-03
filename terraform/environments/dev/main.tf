terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "gcs" {
  source = "../../modules/gcs"

  project_id         = var.project_id
  bucket_name        = var.bucket_name
  location           = var.gcs_location
  force_destroy      = var.gcs_force_destroy
  versioning_enabled = var.gcs_versioning_enabled

  lifecycle_rules = var.gcs_lifecycle_rules

  labels = merge(
    var.common_labels,
    {
      environment = "dev"
      managed_by  = "terraform"
    }
  )
}

module "iam" {
  source = "../../modules/iam"

  project_id   = var.project_id
  account_id   = var.service_account_id
  display_name = var.service_account_display_name
  description  = "Service account for Rakuten search data pipeline"

  project_roles = var.service_account_project_roles

  bucket_roles = {
    rakuten_data = {
      bucket = module.gcs.bucket_name
      role   = "roles/storage.objectAdmin"
    }
  }

  create_key = var.create_service_account_key
}
