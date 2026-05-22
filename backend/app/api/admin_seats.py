from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import Seat, User

router = APIRouter(prefix="/v1/admin/seats", tags=["admin-seats"])


class SeatCreateRequest(BaseModel):
    room_id: int
    seat_code: str
    by_window: bool = False
    has_power: bool = False


class SeatUpdateRequest(BaseModel):
    by_window: bool | None = None
    has_power: bool | None = None
    enabled: bool | None = None


@router.get("")
def list_seats(
    room_id: int | None = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage"))
):
    stmt = select(Seat)
    if room_id is not None:
        stmt = stmt.where(Seat.room_id == room_id)
    return session.exec(stmt).all()


@router.post("")
def create_seat(
    payload: SeatCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage"))
):
    exists = session.exec(
        select(Seat).where(Seat.room_id == payload.room_id, Seat.seat_code == payload.seat_code)
    ).first()
    if exists:
        raise HTTPException(status_code=409, detail="Seat code exists in room")
    seat = Seat(**payload.model_dump())
    session.add(seat)
    session.commit()
    session.refresh(seat)
    return seat


@router.patch("/{seat_id}")
def update_seat(
    seat_id: int,
    payload: SeatUpdateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage"))
):
    seat = session.get(Seat, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(seat, k, v)
    session.add(seat)
    session.commit()
    session.refresh(seat)
    return seat


@router.delete("/{seat_id}")
def delete_seat(
    seat_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("room.manage"))
):
    seat = session.get(Seat, seat_id)
    if not seat:
        raise HTTPException(status_code=404, detail="Seat not found")
    session.delete(seat)
    session.commit()
    return {"ok": True}
