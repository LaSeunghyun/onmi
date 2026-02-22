from __future__ import annotations

from datetime import datetime
from re import match

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, and_, select

from ..db import get_session, init_db
from ..deps import get_current_user
from ..models import NotificationSetting, User


router = APIRouter(prefix="/settings", tags=["settings"])


class NotificationSettingResponse(BaseModel):
    daily_report_time_hhmm: str
    is_enabled: bool


class NotificationSettingUpdate(BaseModel):
    daily_report_time_hhmm: str
    is_enabled: bool


def _validate_hhmm(v: str) -> None:
    if not match(r"^\d{2}:\d{2}$", v):
        raise HTTPException(status_code=400, detail="invalid time (expected HH:MM)")
    hh, mm = v.split(":")
    h = int(hh)
    m = int(mm)
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise HTTPException(status_code=400, detail="invalid time (expected HH:MM)")


@router.get("/notification", response_model=NotificationSettingResponse)
def get_notification_setting(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> NotificationSettingResponse:
    init_db()
    row = session.exec(select(NotificationSetting).where(NotificationSetting.user_id == user.id)).first()
    if not row:
        return NotificationSettingResponse(daily_report_time_hhmm="09:00", is_enabled=True)
    return NotificationSettingResponse(daily_report_time_hhmm=row.daily_report_time_hhmm, is_enabled=row.is_enabled)


@router.put("/notification", response_model=NotificationSettingResponse)
def update_notification_setting(
    body: NotificationSettingUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> NotificationSettingResponse:
    init_db()
    _validate_hhmm(body.daily_report_time_hhmm)
    row = session.exec(select(NotificationSetting).where(NotificationSetting.user_id == user.id)).first()
    now = datetime.now().astimezone()
    if not row:
        row = NotificationSetting(
            user_id=user.id,
            daily_report_time_hhmm=body.daily_report_time_hhmm,
            is_enabled=body.is_enabled,
            updated_at=now,
        )
        session.add(row)
        session.commit()
        session.refresh(row)
    else:
        row.daily_report_time_hhmm = body.daily_report_time_hhmm
        row.is_enabled = body.is_enabled
        row.updated_at = now
        session.add(row)
        session.commit()
        session.refresh(row)

    return NotificationSettingResponse(daily_report_time_hhmm=row.daily_report_time_hhmm, is_enabled=row.is_enabled)

