from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import parse_token
from app.domain.models import User, Role, Permission, UserRoleLink, RolePermissionLink


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1]
    user_id = parse_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_permission(permission_code: str):
    def checker(
        user: User = Depends(get_current_user),
        session: Session = Depends(get_session)
    ) -> User:
        stmt = (
            select(Permission.code)
            .join(RolePermissionLink, RolePermissionLink.permission_id == Permission.id)
            .join(Role, Role.id == RolePermissionLink.role_id)
            .join(UserRoleLink, UserRoleLink.role_id == Role.id)
            .where(UserRoleLink.user_id == user.id)
        )
        user_permissions = set(session.exec(stmt).all())
        if permission_code not in user_permissions:
            raise HTTPException(status_code=403, detail=f"Permission required: {permission_code}")
        return user

    return checker
