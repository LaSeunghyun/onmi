from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# apps/api/.env 를 실행 경로와 무관하게 로드 (Supabase 등 배포 시 동일 동작)
_env_path = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite:///./data/touch.db"

    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expires_minutes: int = 60 * 24 * 7

    # CORS 허용 origins (콤마 구분). 비어있으면 개발 모드로 전체 허용.
    allowed_origins: str = ""

    collector_mode: str = "live"  # live | mock

    processor_mode: str = "mock"  # mock | openai
    openai_api_key: str | None = None

    # 주식 시세·공시 (PRD-stock-signal-notification)
    stock_price_api_key: str = ""  # 공공데이터포털 serviceKey (getStockPriceInfo)
    dart_api_key: str = ""  # DART opendart 인증키
    max_watch_items: int = 10  # 감시종목 최대 등록 수 (PRD §3)


settings = Settings()

