from __future__ import annotations

import logging
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import admin, admin_auth, articles, auth, collect, keywords, me, process, report, settings, stocks
from .settings import settings as app_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if app_settings.jwt_secret == "dev-secret-change-me":
        warnings.warn(
            "JWT_SECRET is using the default value. "
            "Set a secure JWT_SECRET in .env for production.",
            stacklevel=1,
        )
        logger.warning("JWT_SECRET is using the default value — NOT safe for production!")
    init_db()
    yield


app = FastAPI(title="touch API", version="0.1.0", lifespan=lifespan)

_origins: list[str] = (
    [o.strip() for o in app_settings.allowed_origins.split(",") if o.strip()]
    if app_settings.allowed_origins
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin_auth.router)
app.include_router(admin.router)
app.include_router(me.router)
app.include_router(keywords.router)
app.include_router(collect.router)
app.include_router(process.router)
app.include_router(report.router)
app.include_router(articles.router)
app.include_router(settings.router)
app.include_router(stocks.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

