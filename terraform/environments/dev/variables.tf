variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Default GCP region"
  type        = string
  default     = "us-central1"
}

# GCS variables
variable "bucket_name" {
  description = "Name of the GCS bucket for storing JSONL files"
  type        = string
}

variable "gcs_location" {
  description = "Location of the GCS bucket"
  type        = string
  default     = "US"
}

variable "gcs_force_destroy" {
  description = "Allow bucket to be destroyed even if it contains objects"
  type        = bool
  default     = true
}

variable "gcs_versioning_enabled" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = false
}

variable "gcs_lifecycle_rules" {
  description = "List of lifecycle rules for the bucket"
  type = list(object({
    action = object({
      type          = string
      storage_class = optional(string)
    })
    condition = object({
      age                   = optional(number)
      created_before        = optional(string)
      with_state            = optional(string)
      matches_storage_class = optional(list(string))
      num_newer_versions    = optional(number)
    })
  }))
  default = [
    {
      action = {
        type = "Delete"
      }
      condition = {
        age = 90
      }
    }
  ]
}

# IAM variables
variable "service_account_id" {
  description = "Service account ID"
  type        = string
  default     = "rakuten-search-sa"
}

variable "service_account_display_name" {
  description = "Display name for the service account"
  type        = string
  default     = "Rakuten Search Service Account"
}

variable "service_account_project_roles" {
  description = "List of project-level IAM roles to assign to the service account"
  type        = list(string)
  default     = []
}

variable "create_service_account_key" {
  description = "Whether to create a service account key"
  type        = bool
  default     = true
}

# Common labels
variable "common_labels" {
  description = "Common labels to apply to all resources"
  type        = map(string)
  default = {
    project = "rakuten-search"
  }
}
