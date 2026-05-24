from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import SystemParameter, User

router = APIRouter(prefix="/v1/admin/params", tags=["admin-params"])


class ParamUpsertRequest(BaseModel):
    key: str
    value: str


@router.get("")
def list_params(
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    return session.exec(select(SystemParameter)).all()


@router.put("")
def upsert_param(
    payload: ParamUpsertRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("rbac.manage"))
):
    item = session.get(SystemParameter, payload.key)
    if not item:
        item = SystemParameter(key=payload.key, value=payload.value)
    else:
        item.value = payload.value
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
