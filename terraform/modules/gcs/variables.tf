variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "bucket_name" {
  description = "Name of the GCS bucket"
  type        = string
}

variable "location" {
  description = "Location of the GCS bucket"
  type        = string
  default     = "US"
}

variable "force_destroy" {
  description = "Allow bucket to be destroyed even if it contains objects"
  type        = bool
  default     = false
}

variable "versioning_enabled" {
  description = "Enable versioning for the bucket"
  type        = bool
  default     = false
}

variable "lifecycle_rules" {
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
  default = []
}

variable "labels" {
  description = "Labels to apply to the bucket"
  type        = map(string)
  default     = {}
}
