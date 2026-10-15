""MyCDMB FastAPI 入口 — lifespan 自动 bootstrap admin + 注册审计监听器 + 挂载 Web UI"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .api import api_router
from .config import settings
from .core.auth import hash_password
from .core.audit import register_audit_listener
from .db import get_db
from .enums import UserRole
from .models.user import User


def _bootstrap_admin_if_missing(db: Session) -> None:
    existing = db.query(User).filter(User.username == settings.bootstrap_admin_username).first()
    if existing:
        if existing.role != UserRole.ADMIN:
            existing.role = UserRole.ADMIN
            db.commit()
        return
    admin = User(
        username=settings.bootstrap_admin_username,
        hashed_password=hash_password(settings.bootstrap_admin_password),
        full_name='System Bootstrap Admin',
        is_active=True,
        role=UserRole.ADMIN,
    )
    db.add(admin)
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    register_audit_listener()
    db_gen = get_db()
    db: Session = next(db_gen)
    try:
        _bootstrap_admin_if_missing(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description='通信光缆 / 管道 / 杆路 接入资源管理平台',
    lifespan=lifespan,
)

app.include_router(api_router, prefix='/api')


@app.get('/health')
async def health():
    return {'status': 'ok', 'service': settings.app_name, 'version': settings.app_version}


_STATIC_DIR = Path(__file__).resolve().parent.parent / 'static'
if _STATIC_DIR.exists():
    app.mount('/ui', StaticFiles(directory=str(_STATIC_DIR), html=True), name='ui')

    @app.get('/')
    async def root_redirect():
        return FileResponse(str(_STATIC_DIR / 'index.html'))
