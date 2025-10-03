resource "google_service_account" "service_account" {
  account_id   = var.account_id
  display_name = var.display_name
  description  = var.description
  project      = var.project_id
}

resource "google_project_iam_member" "service_account_roles" {
  for_each = toset(var.project_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_storage_bucket_iam_member" "bucket_roles" {
  for_each = var.bucket_roles

  bucket = each.value.bucket
  role   = each.value.role
  member = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_service_account_key" "service_account_key" {
  count = var.create_key ? 1 : 0

  service_account_id = google_service_account.service_account.name
}
