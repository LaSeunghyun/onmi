from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Keyword(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    text: str = Field(index=True)
    is_active: bool = Field(default=True, index=True)
    is_pinned: bool = Field(default=False, index=True)
    last_used_at: Optional[datetime] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone())


class Article(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id", "canonical_url"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    date_kst: str = Field(index=True)  # YYYY-MM-DD

    canonical_url: str = Field(index=True)
    original_url: str

    source_type: str = Field(index=True)  # search_api | rss
    source_name: Optional[str] = Field(default=None, index=True)

    published_at: Optional[datetime] = Field(default=None, index=True)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)

    title_original: str
    snippet_original: Optional[str] = None
    language_original: Optional[str] = Field(default=None, index=True)


class ArticleKeyword(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("article_id", "keyword_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    article_id: UUID = Field(foreign_key="article.id", index=True)
    keyword_id: UUID = Field(foreign_key="keyword.id", index=True)


class ProcessingResult(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("article_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    article_id: UUID = Field(foreign_key="article.id", index=True)

    sentiment: str = Field(index=True)  # positive | neutral | negative
    sentiment_confidence: Optional[float] = None

    summary_original: str
    summary_ko: str

    translated_from: Optional[str] = None
    translation_status: str = Field(index=True)  # not_needed | completed | failed

    created_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)


class NotificationSetting(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("user_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    daily_report_time_hhmm: str = Field(default="09:00", index=True)
    is_enabled: bool = Field(default=True, index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now().astimezone(), index=True)
