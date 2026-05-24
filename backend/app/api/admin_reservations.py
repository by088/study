from datetime import date, datetime, time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, User, Violation

router = APIRouter(prefix="/v1/admin/reservations", tags=["admin-reservations"])


class AdminReservationCreateRequest(BaseModel):
    user_id: str
    room_id: int
    seat_id: int
    reserve_date: date
    start_hour: int
    hours: int
    status: ReservationStatus = ReservationStatus.pending


class AdminReservationUpdateRequest(BaseModel):
    room_id: Optional[int] = None
    seat_id: Optional[int] = None
    reserve_date: Optional[date] = None
    start_hour: Optional[int] = None
    hours: Optional[int] = None
    status: Optional[ReservationStatus] = None


@router.get("")
def list_reservations(
    user_id: Optional[str] = None,
    room_id: Optional[int] = None,
    reserve_date: Optional[date] = None,
    status: Optional[ReservationStatus] = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view"))
):
    stmt = select(Reservation)
    if user_id:
        stmt = stmt.where(Reservation.user_id == user_id)
    if room_id is not None:
        stmt = stmt.where(Reservation.room_id == room_id)
    if reserve_date:
        stmt = stmt.where(Reservation.reserve_date == reserve_date)
    if status:
        stmt = stmt.where(Reservation.status == status)
    return session.exec(stmt.order_by(Reservation.id.desc())).all()


@router.get("/violations")
def list_violation_records(
    user_id: Optional[str] = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view"))
):
    stmt = select(Violation).order_by(Violation.happened_at.desc())
    if user_id:
        stmt = stmt.where(Violation.user_id == user_id)
    return session.exec(stmt).all()


@router.post("")
def create_reservation(
    payload: AdminReservationCreateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view")),
):
    if not session.get(User, payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    reservation = Reservation(
        user_id=payload.user_id,
        room_id=payload.room_id,
        seat_id=payload.seat_id,
        reserve_date=payload.reserve_date,
        start_time=time(payload.start_hour, 0, 0),
        hours=payload.hours,
        status=payload.status,
        checkin_code="0000",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.patch("/{reservation_id}")
def update_reservation(
    reservation_id: int,
    payload: AdminReservationUpdateRequest,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view")),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    data = payload.dict(exclude_unset=True)
    if "start_hour" in data:
        reservation.start_time = time(data.pop("start_hour"), 0, 0)
    for k, v in data.items():
        setattr(reservation, k, v)
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view")),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    session.delete(reservation)
    session.commit()
    return {"ok": True}

