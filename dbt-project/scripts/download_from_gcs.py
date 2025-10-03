"""Download JSONL files from GCS for dbt raw model."""

import os
import sys
from pathlib import Path

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


if __name__ == "__main__":
    bucket_name = os.getenv("GCS_BUCKET_NAME")
    prefix = os.getenv("GCS_FILE_PREFIX", "rakuten_products")
    destination_dir = os.getenv("DOWNLOAD_DIR", "/tmp/gcs_data")

    if not bucket_name:
        print("Error: GCS_BUCKET_NAME environment variable is required")
        sys.exit(1)

    try:
        downloaded_file = download_latest_jsonl(bucket_name, prefix, destination_dir)
        print(f"Success: {downloaded_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
