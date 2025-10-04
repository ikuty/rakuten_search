"""Rakuten Product Search script."""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import requests
from google.cloud import storage

from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RakutenSearchClient:
    """Client for Rakuten Product Search API."""

    def __init__(self, api_key: str):
        """Initialize the client with API key."""
        self.api_key = api_key
        self.endpoint = Config.RAKUTEN_API_ENDPOINT

    def search(
        self,
        keyword: str,
        page: int = 1,
        hits: int = 30,
        shop_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search products on Rakuten.

        Args:
            keyword: Search keyword
            page: Page number
            hits: Number of items per page
            shop_code: Shop code (optional, filters by specific shop)

        Returns:
            API response as dictionary
        """
        params = {
            'applicationId': self.api_key,
            'keyword': keyword,
            'page': page,
            'hits': hits,
            'formatVersion': 2
        }

        # 店舗コードが指定されている場合は追加
        if shop_code:
            params['shopCode'] = shop_code

        # ログメッセージの作成
        log_msg = f"Searching for '{keyword}' (page {page})"
        if shop_code:
            log_msg += f" in shop '{shop_code}'"
        logger.info(log_msg)

        try:
            response = requests.get(self.endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise


class GCSUploader:
    """Uploader for Google Cloud Storage."""

    def __init__(self, bucket_name: str, credentials_path: str):
        """Initialize the uploader."""
        self.client = storage.Client.from_service_account_json(credentials_path)
        self.bucket = self.client.bucket(bucket_name)

    def upload_jsonl(self, data: List[Dict[str, Any]], blob_name: str) -> None:
        """
        Upload data as JSONL to GCS.

        Args:
            data: List of dictionaries to upload
            blob_name: Name of the blob in GCS
        """
        jsonl_content = '\n'.join(json.dumps(item, ensure_ascii=False) for item in data)

        blob = self.bucket.blob(blob_name)
        blob.upload_from_string(jsonl_content, content_type='application/jsonl')

        logger.info(f"Uploaded {len(data)} items to gs://{self.bucket.name}/{blob_name}")


def main():
    """Main execution function."""
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    client = RakutenSearchClient(Config.RAKUTEN_API_KEY)
    uploader = GCSUploader(Config.GCS_BUCKET_NAME, Config.GCS_CREDENTIALS_PATH)

    all_items = []

    # JSTタイムゾーンで現在時刻を取得
    jst_now = datetime.now(ZoneInfo("Asia/Tokyo"))
    year_month = jst_now.strftime("%Y%m")
    year_month_day = jst_now.strftime("%Y%m%d")

    for page in range(1, Config.MAX_PAGES + 1):
        try:
            result = client.search(
                keyword=Config.SEARCH_KEYWORD,
                page=page,
                hits=Config.HITS_PER_PAGE,
                shop_code=Config.SHOP_CODE
            )

            items = result.get('Items', [])
            if not items:
                logger.info("No more items found")
                break

            # Items配列の各要素が直接商品情報を持つ
            all_items.extend(items)

            logger.info(f"Retrieved {len(items)} items from page {page}")

            # レート制限対策: 次のリクエストまで待機
            if page < Config.MAX_PAGES:
                time.sleep(Config.REQUEST_DELAY)

        except Exception as e:
            logger.error(f"Error on page {page}: {e}")
            break

    if all_items:
        # 固定ファイル名: raw/search/yyyymm/search_items_yyyymmdd.jsonl (1日1回上書き)
        blob_name = f"raw/search/{year_month}/search_items_{year_month_day}.jsonl"
        uploader.upload_jsonl(all_items, blob_name)
        logger.info(f"Total items collected: {len(all_items)}")
    else:
        logger.warning("No items collected")


if __name__ == "__main__":
    main()
