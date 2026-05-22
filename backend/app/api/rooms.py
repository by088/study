from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user, require_permission
from app.core.db import get_session
from app.domain.models import StudyRoom, Seat, User

router = APIRouter(prefix="/v1/rooms", tags=["rooms"])


class RoomCreateRequest(BaseModel):
    campus: str
    building: str
    name: str
    opens_at: str = "07:00"
    closes_at: str = "22:00"


@router.get("")
def list_rooms(
    campus: str | None = None,
    has_power: bool | None = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user)
):
    stmt = select(StudyRoom).where(StudyRoom.enabled == True)
    if campus:
        stmt = stmt.where(StudyRoom.campus == campus)
    rooms = session.exec(stmt).all()

    if has_power is None:
        return rooms

    result = []
    for room in rooms:
        seat_stmt = select(Seat).where(Seat.room_id == room.id, Seat.enabled == True)
        seats = session.exec(seat_stmt).all()
        if any(s.has_power for s in seats) == has_power:
            result.append(room)
    return result


@router.post("")
def create_room(
    payload: RoomCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage"))
):
    room = StudyRoom(**payload.model_dump())
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.get("/{room_id}/seats")
def list_room_seats(
    room_id: int,
    by_window: bool | None = None,
    has_power: bool | None = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user)
):
    stmt = select(Seat).where(Seat.room_id == room_id, Seat.enabled == True)
    if by_window is not None:
        stmt = stmt.where(Seat.by_window == by_window)
    if has_power is not None:
        stmt = stmt.where(Seat.has_power == has_power)
    return session.exec(stmt).all()
