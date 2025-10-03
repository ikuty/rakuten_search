FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dbt-postgres and Google Cloud Storage SDK
RUN pip install --no-cache-dir \
    dbt-postgres~=1.7.0 \
    google-cloud-storage>=2.14.0 \
    psycopg2-binary>=2.9.0

# Copy dbt project
COPY . .

CMD ["dbt", "--version"]
