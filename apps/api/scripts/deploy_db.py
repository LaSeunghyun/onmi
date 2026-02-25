r"""
현재 .env의 DATABASE_URL에 스키마(테이블)를 배포하는 스크립트.

사용법:
  cd apps/api
  .\.venv\Scripts\Activate.ps1
  # .env에 DATABASE_URL이 설정되어 있어야 함 (Supabase 또는 로컬 SQLite)
  python -m scripts.deploy_db

환경 변수:
  DATABASE_URL: 연결할 DB (기본 sqlite:///./data/touch.db)
    - Supabase: postgresql://postgres:<PASSWORD>@db.<PROJECT_REF>.supabase.co:5432/postgres?sslmode=require
"""
from __future__ import annotations

import sys
from pathlib import Path

# apps/api 기준으로 app 패키지 로드
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def main() -> None:
    from sqlmodel import SQLModel, create_engine

    from app.models import (
        AdminAuditLog,
        AdminUser,
        AppSetting,
        Article,
        ArticleKeyword,
        CorpCodeCache,
        Keyword,
        MemberAccessLog,
        MemberActionLog,
        MemberProfile,
        NotificationSetting,
        PointAdjustmentRequest,
        ProcessingResult,
        PushToken,
        ServiceModule,
        SignalEventLog,
        SignalRuleConfig,
        StockApiUsageLog,
        User,
        WatchItem,
    )
    from app.settings import settings

    url = (settings.database_url or "").strip()
    if not url or "<PASSWORD>" in url or "<PROJECT_REF>" in url:
        print("오류: .env의 DATABASE_URL을 실제 Supabase(또는 Postgres) 연결 문자열로 설정하세요.")
        print("예: postgresql://postgres:YOUR_PASSWORD@db.xxxx.supabase.co:5432/postgres?sslmode=require")
        sys.exit(1)

    url = _normalize_database_url(url)
    is_sqlite = "sqlite" in url

    engine_kwargs = {}
    if is_sqlite:
        engine_kwargs["connect_args"] = {"check_same_thread": False}
        # SQLite 디렉터리 생성
        if url.startswith("sqlite:///./"):
            rel = url.removeprefix("sqlite:///./")
            Path(rel).parent.mkdir(parents=True, exist_ok=True)
    else:
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 1
        engine_kwargs["max_overflow"] = 0

    engine = create_engine(url, **engine_kwargs)
    print("DB 연결:", "SQLite" if is_sqlite else "Postgres")
    print("스키마 배포 중...")
    SQLModel.metadata.create_all(engine)
    print("스키마 배포 완료.")


if __name__ == "__main__":
    main()
