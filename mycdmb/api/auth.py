""Auth：OAuth2 /token + /me + /register (admin only)"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..core.auth import authenticate_user, create_access_token, require_admin, get_current_user, hash_password
from ..db import get_db
from ..enums import UserRole
from ..models.user import User

router = APIRouter(prefix='/auth', tags=['auth'])


class Token(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    role: UserRole = UserRole.VIEWER


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: str | None = None
    is_active: bool
    role: UserRole


@router.post('/login', response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail='用户名或密码错误')
    return {'access_token': create_access_token(user.id), 'token_type': 'bearer'}


@router.get('/me', response_model=UserResponse)
def me(current: User = Depends(get_current_user)):
    return current


@router.post('/register', response_model=UserResponse, status_code=201)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail='用户名已存在')
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
