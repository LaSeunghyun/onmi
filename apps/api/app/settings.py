from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./data/touch.db"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 60 * 24 * 7

    collector_mode: str = "live"  # live | mock

    processor_mode: str = "mock"  # mock | openai
    openai_api_key: str | None = None

    # 주식 시세·공시 (PRD-stock-signal-notification)
    stock_price_api_key: str = ""  # 공공데이터포털 serviceKey (getStockPriceInfo)
    dart_api_key: str = ""  # DART opendart 인증키


settings = Settings()

