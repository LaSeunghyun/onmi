from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .models import Article
from .settings import settings


@dataclass(frozen=True)
class Processed:
    sentiment: str
    sentiment_confidence: Optional[float]
    summary_original: str
    summary_ko: str
    translated_from: Optional[str]
    translation_status: str


def process_article_mock(article: Article) -> Processed:
    title = article.title_original.strip()
    summary_original = article.snippet_original.strip() if article.snippet_original else f"Summary: {title}"
    lang = (article.language_original or "").lower()

    if lang and lang.startswith("ko"):
        return Processed(
            sentiment="neutral",
            sentiment_confidence=0.5,
            summary_original=summary_original,
            summary_ko=summary_original,
            translated_from=None,
            translation_status="not_needed",
        )

    # 원문 기준(영문 등) 처리 후 한국어 번역 표시라는 형태만 유지
    return Processed(
        sentiment="neutral",
        sentiment_confidence=0.5,
        summary_original=summary_original,
        summary_ko=f"(번역) {summary_original}",
        translated_from=article.language_original or "unknown",
        translation_status="completed",
    )


def process_article(article: Article) -> Processed:
    mode = (settings.processor_mode or "mock").lower()
    if mode == "mock":
        return process_article_mock(article)

    # Step 11에서는 외부 키가 없어도 개발이 진행되도록 mock을 기본 제공한다.
    # openai 등 실서비스 모드는 다음 단계에서 키 주입 시 확장한다.
    return process_article_mock(article)

