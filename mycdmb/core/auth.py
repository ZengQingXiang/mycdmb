""认证：bcrypt 哈希 + python-jose JWT + require_role 依赖工厂"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated, Callable

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..db import get_db
from ..enums import UserRole
from ..models.user import User
from .audit import setup_audit


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def create_access_token(subject: str | int, expires_delta: timedelta | None = None) -> str:
    from ..config import settings
    to_encode = {'sub': str(subject)}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode['exp'] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if user and user.is_active and verify_password(password, user.hashed_password):
        return user
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    from fastapi.security import OAuth2PasswordBearer
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)
    token = None
    auth = request.headers.get('authorization')
    if auth and auth.startswith('Bearer '):
        token = auth[7:]
    if not token:
        token = oauth2_scheme(request)
    if not token:
        raise HTTPException(status_code=401, detail='Not authenticated')
    try:
        from ..config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail='User inactive')
    setup_audit(db, user, request)
    return user


def require_role(*allowed: UserRole) -> Callable:
    """返回一个 FastAPI 依赖：既做鉴权，又 setup_audit。"""
    def _dep(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed:
            raise HTTPException(status_code=403, detail='Forbidden')
        return current_user
    return _dep


require_write = require_role(UserRole.ADMIN, UserRole.OPERATOR)
require_admin = require_role(UserRole.ADMIN)
