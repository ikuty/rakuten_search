variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "account_id" {
  description = "Service account ID"
  type        = string
}

variable "display_name" {
  description = "Display name for the service account"
  type        = string
}

variable "description" {
  description = "Description of the service account"
  type        = string
  default     = ""
}

variable "project_roles" {
  description = "List of project-level IAM roles to assign to the service account"
  type        = list(string)
  default     = []
}

variable "bucket_roles" {
  description = "Map of bucket-specific IAM roles to assign to the service account"
  type = map(object({
    bucket = string
    role   = string
  }))
  default = {}
}

variable "create_key" {
  description = "Whether to create a service account key"
  type        = bool
  default     = true
}
