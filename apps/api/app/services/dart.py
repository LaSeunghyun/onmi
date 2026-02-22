"""DART opendart 공시검색 API (list.json). corp_code 8자리 기준."""
from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from ..settings import settings

LIST_URL = "https://opendart.fss.or.kr/api/list.json"


def _parse_item(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "corp_code": raw.get("corp_code") or "",
        "corp_name": raw.get("corp_name") or "",
        "report_nm": raw.get("report_nm") or "",
        "rcept_no": raw.get("rcept_no") or "",
        "rcept_dt": raw.get("rcept_dt") or "",
        "flr_nm": raw.get("flr_nm") or "",
    }


class DartDisclosure:
    def __init__(self, data: dict[str, Any]) -> None:
        self.corp_code = data.get("corp_code") or ""
        self.corp_name = data.get("corp_name") or ""
        self.report_nm = data.get("report_nm") or ""
        self.rcept_no = data.get("rcept_no") or ""
        self.rcept_dt = data.get("rcept_dt") or ""
        self.flr_nm = data.get("flr_nm") or ""


class DartClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = (api_key or settings.dart_api_key or "").strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def fetch_list(
        self,
        corp_code: str,
        *,
        bgn_de: str | None = None,
        end_de: str | None = None,
        page_no: int = 1,
        page_count: int = 10,
    ) -> list[DartDisclosure]:
        """공시대상회사 고유번호(corp_code 8자리) 기준 공시 목록 조회."""
        if not self.api_key:
            return []
        end = end_de or datetime.now().strftime("%Y%m%d")
        bgn = bgn_de or (datetime.now().strftime("%Y%m%d"))
        params: dict[str, str | int] = {
            "crtfc_key": self.api_key,
            "corp_code": corp_code.strip(),
            "bgn_de": bgn,
            "end_de": end,
            "page_no": page_no,
            "page_count": min(page_count, 100),
        }
        try:
            with httpx.Client(timeout=15.0) as client:
                r = client.get(LIST_URL, params=params)
                r.raise_for_status()
        except Exception:
            return []

        data = r.json()
        status = data.get("status")
        if status and status != "000":
            return []

        raw_list = data.get("list") or []
        return [DartDisclosure(_parse_item(it)) for it in raw_list]
