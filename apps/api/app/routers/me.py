from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import get_current_user
from ..models import User, UserPublic


router = APIRouter(tags=["me"])


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(user)

