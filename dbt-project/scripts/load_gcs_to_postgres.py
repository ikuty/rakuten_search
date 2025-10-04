"""Load JSONL data from GCS to PostgreSQL."""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg2
from google.cloud import storage


def download_jsonl_for_date(bucket_name: str, destination_dir: str, execution_date: datetime) -> tuple[str, str]:
    """
    Download JSONL file from GCS for the specified execution date.

    File path format: raw/search/yyyymm/search_items_yyyymmdd.jsonl

    Args:
        bucket_name: GCS bucket name
        destination_dir: Local directory to save the file
        execution_date: Execution date (JST)

    Returns:
        Tuple of (downloaded file path, yyyymmdd string)
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    year_month = execution_date.strftime("%Y%m")
    year_month_day = execution_date.strftime("%Y%m%d")

    # 固定ファイル名: raw/search/yyyymm/search_items_yyyymmdd.jsonl
    blob_name = f"raw/search/{year_month}/search_items_{year_month_day}.jsonl"
    blob = bucket.blob(blob_name)

    if not blob.exists():
        raise ValueError(f"File not found: gs://{bucket_name}/{blob_name}")

    # Create destination directory if not exists
    dest_dir = Path(destination_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Download the file
    destination_path = dest_dir / f"search_items_{year_month_day}.jsonl"
    blob.download_to_filename(str(destination_path))

    print(f"Downloaded: gs://{bucket_name}/{blob_name} -> {destination_path}")
    return str(destination_path), year_month_day


def load_jsonl_to_postgres(
    file_path: str,
    execution_date: datetime,
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    schema: str = 'public_raw',
    table: str = 'rakuten_products_raw'
):
    """
    Load JSONL file to PostgreSQL with idempotency.
    Deletes existing records with the same loaded_at date before inserting.

    Args:
        file_path: Path to JSONL file
        execution_date: Execution date (JST)
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

        # 冪等性のため、実行日付に該当するレコードを削除
        execution_date_start = execution_date.replace(hour=0, minute=0, second=0, microsecond=0)
        execution_date_end = execution_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        cur.execute(
            f"DELETE FROM {schema}.{table} WHERE loaded_at >= %s AND loaded_at <= %s",
            (execution_date_start, execution_date_end)
        )
        deleted_count = cur.rowcount
        if deleted_count > 0:
            print(f"Deleted {deleted_count} existing records for date {execution_date.strftime('%Y%m%d')}")

        # 処理実行時のタイムスタンプを取得(JST)
        jst_now = execution_date

        # Load JSONL data
        with open(file_path, 'r', encoding='utf-8') as f:
            count = 0
            for line in f:
                if line.strip():
                    cur.execute(
                        f"INSERT INTO {schema}.{table} (data, loaded_at) VALUES (%s, %s)",
                        (line.strip(), jst_now)
                    )
                    count += 1

        conn.commit()
        print(f"Loaded {count} records into {schema}.{table} at {jst_now}")

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
        # 実行日付(JST)を取得
        execution_date = datetime.now(ZoneInfo("Asia/Tokyo"))
        print(f"Execution date (JST): {execution_date.strftime('%Y%m%d')}")

        # Download file for execution date from GCS
        print("Downloading file from GCS...")
        file_path, yyyymmdd = download_jsonl_for_date(bucket_name, destination_dir, execution_date)

        # Load to PostgreSQL with idempotency
        print("Loading data to PostgreSQL...")
        load_jsonl_to_postgres(
            file_path=file_path,
            execution_date=execution_date,
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
