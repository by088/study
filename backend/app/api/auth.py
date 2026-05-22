from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.security import hash_password, verify_password, issue_token
from app.domain.models import User

router = APIRouter(prefix="/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    user_id: str
    name: str
    password: str
    email: EmailStr


class LoginRequest(BaseModel):
    user_id: str
    password: str


@router.post("/register")
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    exists = session.get(User, payload.user_id)
    if exists:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        id=payload.user_id,
        name=payload.name,
        password_hash=hash_password(payload.password),
        email=payload.email
    )
    session.add(user)
    session.commit()
    return {"ok": True, "user_id": user.id}


@router.post("/login")
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.get(User, payload.user_id)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"ok": True, "token": issue_token(user.id), "profile": {"id": user.id, "name": user.name}}


@router.get("/me")
def me(current: User = Depends(get_current_user)):
    return {
        "id": current.id,
        "name": current.name,
        "credit_score": current.credit_score,
        "default_count": current.default_count
    }
