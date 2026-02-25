from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_db
from .routers import admin, admin_auth, articles, auth, collect, keywords, me, process, report, settings, stocks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="touch API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

