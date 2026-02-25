r"""
로컬 SQLite DB → Supabase Postgres 이전 스크립트.

사용법:
  cd apps/api
  .\.venv\Scripts\Activate.ps1
  # Supabase 연결 문자열 설정 (비밀번호 치환, ?sslmode=require 포함)
  $env:TARGET_DATABASE_URL = "postgresql://postgres:YOUR_PASSWORD@db.jodarpqalwttovzsdnts.supabase.co:5432/postgres?sslmode=require"
  python -m scripts.migrate_sqlite_to_supabase

환경 변수:
  SOURCE_DATABASE_URL: 로컬 SQLite (기본 sqlite:///./data/touch.db, apps/api 기준)
  TARGET_DATABASE_URL: Supabase Postgres URI (필수)

주의: Supabase는 빈 DB이거나 이 스크립트로만 채울 때 사용. 이미 데이터가 있으면 PK 중복 오류가 납니다.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# apps/api 기준으로 app 패키지 로드
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _normalize_postgres_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def main() -> None:
    from sqlmodel import Session, SQLModel, create_engine, select

    from app.models import (
        AdminAuditLog,
        AdminUser,
        AppSetting,
        Article,
        ArticleKeyword,
        CorpCodeCache,
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
        Keyword,
    )

    source_url = os.getenv("SOURCE_DATABASE_URL", "sqlite:///./data/touch.db").strip()
    target_url = os.getenv("TARGET_DATABASE_URL", "").strip()
    if not target_url:
        print("TARGET_DATABASE_URL 환경 변수를 설정하세요 (Supabase Postgres URI).")
        sys.exit(1)
    target_url = _normalize_postgres_url(target_url)

    # FK 순서: 부모 테이블 먼저
    model_order = [
        User,
        AdminUser,
        ServiceModule,
        AppSetting,
        StockApiUsageLog,
        CorpCodeCache,
        Keyword,
        Article,
        ArticleKeyword,
        ProcessingResult,
        NotificationSetting,
        MemberProfile,
        MemberAccessLog,
        MemberActionLog,
        WatchItem,
        SignalRuleConfig,
        PushToken,
        SignalEventLog,
        AdminAuditLog,
        PointAdjustmentRequest,
    ]

    source_engine = create_engine(
        source_url,
        connect_args={"check_same_thread": False} if "sqlite" in source_url else {},
    )
    target_engine = create_engine(
        target_url,
        connect_args={} if "sqlite" in target_url else {},
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )

    # 1) Supabase에 스키마 생성
    print("Supabase에 스키마 생성 중...")
    SQLModel.metadata.create_all(target_engine)
    print("스키마 생성 완료.")

    # 2) 테이블별 데이터 복사
    for model in model_order:
        table_name = model.__tablename__
        with Session(source_engine) as src_session:
            rows = list(src_session.exec(select(model)).all())
        if not rows:
            print(f"  {table_name}: 0건 (건너뜀)")
            continue
        with Session(target_engine) as dst_session:
            for row in rows:
                dst_session.add(model.model_validate(row.model_dump()))
            dst_session.commit()
        print(f"  {table_name}: {len(rows)}건 복사 완료.")

    print("마이그레이션 완료.")


if __name__ == "__main__":
    main()
