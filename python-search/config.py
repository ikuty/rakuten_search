"""Configuration module for Rakuten Product Search."""

import os
from typing import Optional


class Config:
    """Configuration class for Rakuten API and GCS settings."""

    # Rakuten API settings
    RAKUTEN_API_KEY: str = os.getenv("RAKUTEN_API_KEY", "")
    RAKUTEN_API_ENDPOINT: str = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"

    # GCS settings
    GCS_BUCKET_NAME: str = os.getenv("GCS_BUCKET_NAME", "")
    GCS_CREDENTIALS_PATH: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Search parameters
    SEARCH_KEYWORD: str = os.getenv("SEARCH_KEYWORD", "ノートパソコン")
    SHOP_CODE: Optional[str] = os.getenv("SHOP_CODE")  # 店舗コード（オプション）
    HITS_PER_PAGE: int = int(os.getenv("HITS_PER_PAGE", "30"))
    MAX_PAGES: int = int(os.getenv("MAX_PAGES", "10"))
    REQUEST_DELAY: float = float(os.getenv("REQUEST_DELAY", "1.0"))

    # Output settings
    OUTPUT_PREFIX: str = os.getenv("OUTPUT_PREFIX", "rakuten_products")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.RAKUTEN_API_KEY:
            raise ValueError("RAKUTEN_API_KEY is required")
        if not cls.GCS_BUCKET_NAME:
            raise ValueError("GCS_BUCKET_NAME is required")
        if not cls.GCS_CREDENTIALS_PATH:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is required")
