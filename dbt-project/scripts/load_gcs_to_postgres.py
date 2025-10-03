"""Load JSONL data from GCS to PostgreSQL."""

import json
import os
import sys
from pathlib import Path

import psycopg2
from google.cloud import storage


def download_latest_jsonl(bucket_name: str, prefix: str, destination_dir: str) -> str:
    """
    Download the latest JSONL file from GCS.

    Args:
        bucket_name: GCS bucket name
        prefix: Prefix to filter blobs
        destination_dir: Local directory to save the file

    Returns:
        Path to downloaded file
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # List all blobs with the given prefix
    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
        raise ValueError(f"No files found with prefix '{prefix}' in bucket '{bucket_name}'")

    # Sort by time_created and get the latest
    latest_blob = max(blobs, key=lambda b: b.time_created)

    # Create destination directory if not exists
    dest_dir = Path(destination_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Download the file
    destination_path = dest_dir / latest_blob.name.split('/')[-1]
    latest_blob.download_to_filename(str(destination_path))

    print(f"Downloaded: {latest_blob.name} -> {destination_path}")
    return str(destination_path)


def load_jsonl_to_postgres(
    file_path: str,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    schema: str = 'public_raw',
    table: str = 'rakuten_products_raw'
):
    """
    Load JSONL file to PostgreSQL.

    Args:
        file_path: Path to JSONL file
        db_host: PostgreSQL host
        db_port: PostgreSQL port
        db_name: Database name
        db_user: Database user
        db_password: Database password
        schema: Schema name
        table: Table name
    """
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()

    try:
        # Create schema if not exists
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        # Create table if not exists
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema}.{table} (
                data JSONB,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Truncate existing data (optional - comment out if you want to append)
        cur.execute(f"TRUNCATE TABLE {schema}.{table}")

        # Load JSONL data
        with open(file_path, 'r', encoding='utf-8') as f:
            count = 0
            for line in f:
                if line.strip():
                    cur.execute(
                        f"INSERT INTO {schema}.{table} (data) VALUES (%s)",
                        (line.strip(),)
                    )
                    count += 1

        conn.commit()
        print(f"Loaded {count} records into {schema}.{table}")

    except Exception as e:
        conn.rollback()
        print(f"Error loading data: {e}")
        raise
    finally:
        cur.close()
        conn.close()


def main():
    """Main execution function."""
    # GCS settings
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    prefix = os.getenv("GCS_FILE_PREFIX", "rakuten_products")
    destination_dir = os.getenv("DOWNLOAD_DIR", "/tmp/gcs_data")

    # PostgreSQL settings
    db_host = os.getenv("POSTGRES_HOST", "postgres")
    db_port = int(os.getenv("POSTGRES_PORT", "5432"))
    db_name = os.getenv("POSTGRES_DB", "rakuten_data")
    db_user = os.getenv("POSTGRES_USER", "datauser")
    db_password = os.getenv("POSTGRES_PASSWORD")

    if not bucket_name:
        print("Error: GCS_BUCKET_NAME environment variable is required")
        sys.exit(1)

    if not db_password:
        print("Error: POSTGRES_PASSWORD environment variable is required")
        sys.exit(1)

    try:
        # Download latest file from GCS
        print("Downloading latest file from GCS...")
        file_path = download_latest_jsonl(bucket_name, prefix, destination_dir)

        # Load to PostgreSQL
        print("Loading data to PostgreSQL...")
        load_jsonl_to_postgres(
            file_path=file_path,
            db_host=db_host,
            db_port=db_port,
            db_name=db_name,
            db_user=db_user,
            db_password=db_password
        )

        print("Success!")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
