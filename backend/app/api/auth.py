from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.security import hash_password, verify_password, issue_token
from sqlmodel import select
from app.domain.models import Role, User, UserRoleLink

router = APIRouter(prefix="/v1/auth", tags=["auth"])
legacy_router = APIRouter(tags=["auth-legacy"])


class RegisterRequest(BaseModel):
    user_id: str
    name: str
    password: str
    email: EmailStr
    department: str = None


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
        email=payload.email,
        department=payload.department,
    )
    session.add(user)
    session.commit()
    student_role = session.exec(select(Role).where(Role.code == "student")).first()
    if student_role and not session.get(UserRoleLink, (user.id, student_role.id)):
        session.add(UserRoleLink(user_id=user.id, role_id=student_role.id))
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
        "department": current.department,
        "credit_score": current.credit_score,
        "default_count": current.default_count,
    }


@legacy_router.post("/v1/register")
def legacy_register(payload: RegisterRequest, session: Session = Depends(get_session)):
    user = session.get(User, payload.user_id)
    if user:
        return {"success": False, "code": 301, "message": "User is existing"}
    user = User(
        id=payload.user_id,
        name=payload.name,
        password_hash=hash_password(payload.password),
        email=payload.email,
        department=payload.department,
    )
    session.add(user)
    session.commit()
    student_role = session.exec(select(Role).where(Role.code == "student")).first()
    if student_role and not session.get(UserRoleLink, (user.id, student_role.id)):
        session.add(UserRoleLink(user_id=user.id, role_id=student_role.id))
        session.commit()
    token = issue_token(user.id)
    return {"success": True, "code": 100, "token": token}


@legacy_router.post("/v1/login")
def legacy_login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.get(User, payload.user_id)
    if not user:
        return {"success": False, "code": 201, "message": "User not found"}
    if not verify_password(payload.password, user.password_hash):
        return {"success": False, "code": 202, "message": "Incorrect password"}
    token = issue_token(user.id)
    return {
        "success": True,
        "code": 100,
        "token": token,
        "data": {
            "user_id": user.id,
            "userName": user.name,
            "credits": user.credit_score,
            "defaultTimes": user.default_count,
            "email": user.email,
        },
    }


@legacy_router.get("/v1/userInfo")
def legacy_user_info(current: User = Depends(get_current_user)):
    return {
        "success": True,
        "code": 100,
        "data": {
            "user_id": current.id,
            "user_name": current.name,
            "email": current.email,
            "department": current.department,
            "credits": current.credit_score,
            "default_times": current.default_count,
        },
    }
