from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import StudyRoom, User

router = APIRouter(prefix="/v1/admin/rooms", tags=["admin-rooms"])


class RoomCreateRequest(BaseModel):
    campus: str
    building: str
    name: str
    department: str = None
    open_to_all: bool = True
    opens_at: str = "07:00"
    closes_at: str = "22:00"
    enabled: bool = True


class RoomUpdateRequest(BaseModel):
    campus: Optional[str] = None
    building: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    open_to_all: Optional[bool] = None
    opens_at: Optional[str] = None
    closes_at: Optional[str] = None
    enabled: Optional[bool] = None


@router.get("")
def list_rooms(
    campus: Optional[str] = None,
    building: Optional[str] = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage")),
):
    stmt = select(StudyRoom)
    if campus:
        stmt = stmt.where(StudyRoom.campus == campus)
    if building:
        stmt = stmt.where(StudyRoom.building == building)
    return session.exec(stmt.order_by(StudyRoom.id.desc())).all()


@router.post("")
def create_room(
    payload: RoomCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage")),
):
    exists = session.exec(
        select(StudyRoom).where(
            StudyRoom.campus == payload.campus,
            StudyRoom.building == payload.building,
            StudyRoom.name == payload.name,
        )
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Room already exists")
    room = StudyRoom(**payload.dict())
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.patch("/{room_id}")
def update_room(
    room_id: int,
    payload: RoomUpdateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage")),
):
    room = session.get(StudyRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(room, k, v)
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.delete("/{room_id}")
def delete_room(
    room_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage")),
):
    room = session.get(StudyRoom, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.enabled = False
    session.add(room)
    session.commit()
    return {"ok": True}
