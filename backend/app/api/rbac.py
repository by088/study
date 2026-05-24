from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import Role, Permission, UserRoleLink, RolePermissionLink, User

router = APIRouter(prefix="/v1/rbac", tags=["rbac"])


class RoleCreateRequest(BaseModel):
    code: str
    name: str


class AssignRoleRequest(BaseModel):
    user_id: str
    role_code: str


class GrantPermissionRequest(BaseModel):
    role_code: str
    permission_code: str


@router.get("/roles")
def list_roles(
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    return session.exec(select(Role)).all()


@router.post("/roles")
def create_role(
    payload: RoleCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    if session.exec(select(Role).where(Role.code == payload.code)).first():
        raise HTTPException(status_code=409, detail="Role code exists")
    role = Role(code=payload.code, name=payload.name)
    session.add(role)
    session.commit()
    session.refresh(role)
    return role


@router.post("/assign-role")
def assign_role(
    payload: AssignRoleRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    user = session.get(User, payload.user_id)
    role = session.exec(select(Role).where(Role.code == payload.role_code)).first()
    if not user or not role:
        raise HTTPException(status_code=404, detail="User or role not found")

    link = session.get(UserRoleLink, (user.id, role.id))
    if link:
        return {"ok": True, "message": "already assigned"}

    session.add(UserRoleLink(user_id=user.id, role_id=role.id))
    session.commit()
    return {"ok": True}


@router.post("/grant")
def grant_permission(
    payload: GrantPermissionRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    role = session.exec(select(Role).where(Role.code == payload.role_code)).first()
    perm = session.exec(select(Permission).where(Permission.code == payload.permission_code)).first()
    if not role or not perm:
        raise HTTPException(status_code=404, detail="Role or permission not found")

    link = session.get(RolePermissionLink, (role.id, perm.id))
    if link:
        return {"ok": True, "message": "already granted"}

    session.add(RolePermissionLink(role_id=role.id, permission_id=perm.id))
    session.commit()
    return {"ok": True}
