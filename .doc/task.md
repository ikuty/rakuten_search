# Task Management

## Task 1: Documentation
- [x] Create .doc/design.md
- [x] Create .doc/task.md

## Task 2: Terraform Infrastructure
- [x] Create GCS module
  - [x] terraform/modules/gcs/main.tf
  - [x] terraform/modules/gcs/variables.tf
  - [x] terraform/modules/gcs/outputs.tf
- [x] Create IAM module
  - [x] terraform/modules/iam/main.tf
  - [x] terraform/modules/iam/variables.tf
  - [x] terraform/modules/iam/outputs.tf
- [x] Create dev environment
  - [x] terraform/environments/dev/main.tf
  - [x] terraform/environments/dev/variables.tf
  - [x] terraform/environments/dev/terraform.tfvars
  - [x] terraform/environments/dev/outputs.tf

## Task 3: SSH Bastion
- [x] Create ssh-bastion/Dockerfile
- [x] Create ssh-bastion/sshd_config
- [x] Create ssh-bastion/entrypoint.sh

## Task 4: SSH Key Management
- [x] Create ssh-keys/.gitkeep
- [x] Create ssh-keys/README.md
- [x] Update .gitignore

## Task 5: Docker Compose
- [x] Create docker-compose.yml
  - [x] postgres service
  - [x] ssh-bastion service
  - [x] python-search service
  - [x] dbt service

## Task 6: Python Search Environment
- [x] Create python-search/Dockerfile
- [x] Create python-search/requirements.txt
- [x] Create python-search/config.py
- [x] Create python-search/search.py

## Task 7: dbt Environment
- [x] Create dbt-project/Dockerfile
- [x] Create dbt-project/dbt_project.yml
- [x] Create dbt-project/profiles.yml
- [x] Create dbt-project/scripts/download_from_gcs.py
- [x] Create dbt-project/models/raw/
  - [x] rakuten_products_raw.sql
  - [x] schema.yml
- [x] Create dbt-project/models/staging/
  - [x] stg_rakuten_products.sql
  - [x] schema.yml
- [x] Create dbt-project/models/intermediate/
  - [x] int_products_enriched.sql
  - [x] schema.yml
- [x] Create dbt-project/models/mart/
  - [x] dim_products.sql
  - [x] schema.yml

## Task 8: Environment Variables
- [x] Create .env.example
- [x] Update .gitignore

## Task 9: README
- [x] Create README.md
  - [x] Project overview
  - [x] Prerequisites
  - [x] Setup instructions
  - [x] Usage instructions
  - [x] Troubleshooting

## Task 10: Version Control
- [x] Update .gitignore
  - [x] Python cache files
  - [x] dbt artifacts
  - [x] SSH keys
  - [x] Environment files
  - [x] Terraform state
  - [x] GCP credentials
