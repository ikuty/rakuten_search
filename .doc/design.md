# Design Document: Rakuten Product Search Data Pipeline

## Overview

This project implements a data pipeline that:
1. Fetches product data from Rakuten Product Search API
2. Stores raw data as JSONL files in Google Cloud Storage (GCS)
3. Loads and transforms the data using dbt
4. Stores the processed data in PostgreSQL

## Architecture

```
Rakuten API → Python Script → GCS (JSONL)
                                 ↓ (load script)
                              PostgreSQL (externally accessible)
                           (raw → staging → intermediate → mart)
                                 ↑
                              Terraform (GCP Resources)
```

## Infrastructure Components

### 1. Terraform Infrastructure

#### Module Structure
```
terraform/
├── environments/
│   └── dev/              # Development environment configuration
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars
│       └── outputs.tf
└── modules/
    ├── gcs/              # GCS bucket module
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── iam/              # Service account and IAM module
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

#### Resources Managed
- **GCS Bucket**: Storage for JSONL files with lifecycle policies
- **Service Account**: For Python/dbt to access GCS
- **IAM Roles**: Minimal permissions (Storage Object Admin)

### 2. Docker Compose Services

#### postgres
- PostgreSQL database server
- Port 5432 exposed for external access
- Data persistence via Docker volume

#### python-search
- Python runtime environment
- Executes Rakuten API search
- Uploads JSONL to GCS
- Dependencies: requests, google-cloud-storage

#### dbt
- dbt runtime environment with PostgreSQL adapter
- Includes Google Cloud Storage SDK
- Executes data transformations
- Pre-hook downloads JSONL from GCS

### 3. Data Layer Architecture

#### dbt Model Layers

**raw**
- Purpose: Load raw JSONL data from GCS into PostgreSQL
- Pre-hook: Execute `download_from_gcs.py` to fetch JSONL files
- Load method: PostgreSQL `COPY` command or `INSERT` from JSON
- Schema: Minimal, stores raw JSON structure

**staging**
- Purpose: Basic data cleaning and normalization
- Operations:
  - Data type conversion
  - NULL handling
  - Column name standardization
  - Extract nested JSON fields
- Schema: Flattened structure with proper data types

**intermediate**
- Purpose: Apply business logic and create reusable components
- Operations:
  - Data enrichment
  - Calculated fields
  - Joins between staging models
  - Aggregations
- Schema: Business-oriented structure

**mart**
- Purpose: Final analytical tables for consumption
- Operations:
  - Dimension tables
  - Fact tables
  - Denormalized views for analysis
- Schema: Optimized for queries and reporting

## Data Flow

1. **Data Collection**
   - Python script calls Rakuten Product Search API
   - Search parameters configured via environment variables
   - Results saved as JSONL format (one JSON object per line)
   - Upload to GCS bucket

2. **Data Loading**
   - Execute `load_gcs_to_postgres.py` script
   - Script downloads latest JSONL from GCS
   - Loads data into PostgreSQL raw table

3. **Data Transformation**
   - dbt runs models in dependency order
   - raw → staging: Data cleaning and type conversion
   - staging → intermediate: Business logic application
   - intermediate → mart: Final analytical tables

4. **Data Access**
   - Direct access to PostgreSQL on port 5432
   - Connection: `psql -h localhost -p 5432 -U datauser -d rakuten_data`
   - GUI clients (DBeaver, pgAdmin) can connect directly

## Security Requirements

### Database Access Control
- PostgreSQL port 5432 exposed for external access
- Access controlled by username/password authentication
- Consider using firewall rules or VPN for production environments

### GCP Authentication
- Service account key file for GCS access
- Stored outside repository (referenced via environment variable)
- Minimal IAM permissions (Storage Object Admin only)

## Environment Variables

```
# Rakuten API
RAKUTEN_API_KEY=<your-api-key>

# GCP
GCP_PROJECT_ID=<your-project-id>
GCS_BUCKET_NAME=<bucket-name>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=rakuten_data
POSTGRES_USER=datauser
POSTGRES_PASSWORD=<secure-password>

# SSH
SSH_USER=sshuser
```

## File Formats

### JSONL Format
- One JSON object per line
- Example:
```jsonl
{"itemCode": "ABC123", "itemName": "Product A", "itemPrice": 1000}
{"itemCode": "DEF456", "itemName": "Product B", "itemPrice": 2000}
```

### Rakuten API Response Structure
Refer to Rakuten API documentation for detailed schema:
https://webservice.rakuten.co.jp/documentation/ichiba-item-search

## Development Workflow

1. Infrastructure setup: `terraform apply`
2. Generate SSH keys: `ssh-keygen -t rsa -b 4096 -f ssh-keys/id_rsa`
3. Start services: `docker-compose up -d`
4. Run Python search: `docker-compose run python-search python search.py`
5. Run dbt: `docker-compose run dbt dbt run`
6. Access database: SSH port forward + psql/DBeaver

## Future Enhancements

- Incremental loading strategy for large datasets
- Data quality tests in dbt
- Orchestration with Airflow/Prefect
- Multi-environment support (dev/staging/prod)
- Monitoring and alerting
- CI/CD pipeline for dbt models
