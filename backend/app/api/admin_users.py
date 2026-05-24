from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.core.security import hash_password
from app.domain.models import User, Violation, Reservation

router = APIRouter(prefix="/v1/admin/users", tags=["admin-users"])


class UserCreateRequest(BaseModel):
    id: str
    name: str
    password: str
    email: EmailStr
    department: str = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    department: Optional[str] = None
    credit_score: Optional[int] = None


@router.get("")
def list_users(
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    return session.exec(select(User).order_by(User.created_at.desc())).all()


@router.post("")
def create_user(
    payload: UserCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    if session.get(User, payload.id):
        raise HTTPException(status_code=409, detail="User id exists")
    user = User(
        id=payload.id,
        name=payload.name,
        password_hash=hash_password(payload.password),
        email=payload.email,
        department=payload.department,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/{user_id}")
def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(user, k, v)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}


@router.get("/violations")
def list_violations(
    user_id: Optional[str] = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view"))
):
    stmt = select(Violation).order_by(Violation.happened_at.desc())
    if user_id:
        stmt = stmt.where(Violation.user_id == user_id)
    return session.exec(stmt).all()

