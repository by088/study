from datetime import datetime, date, time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user, require_permission
from app.core.config import settings
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, Seat, StudyRoom, User
from app.domain.rules import validate_hourly_slot

router = APIRouter(prefix="/v1/reservations", tags=["reservations"])


class ReservationCreateRequest(BaseModel):
    room_id: int
    seat_id: int
    reserve_date: date
    start_hour: int
    hours: int


@router.post("")
def create_reservation(
    payload: ReservationCreateRequest,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    if current.credit_score < settings.min_credit_score:
        raise HTTPException(status_code=400, detail="Credit score too low")

    start_at = datetime.combine(payload.reserve_date, time(payload.start_hour, 0, 0))
    try:
        validate_hourly_slot(start_at, payload.hours, settings.max_reservation_hours)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    seat = session.get(Seat, payload.seat_id)
    if not seat or seat.room_id != payload.room_id or not seat.enabled:
        raise HTTPException(status_code=404, detail="Seat not found")

    same_day_pending = session.exec(
        select(Reservation).where(
            Reservation.user_id == current.id,
            Reservation.reserve_date == payload.reserve_date,
            Reservation.status == ReservationStatus.pending
        )
    ).first()
    if same_day_pending:
        raise HTTPException(status_code=400, detail="Only one pending reservation per day")

    conflicts = session.exec(
        select(Reservation).where(
            Reservation.seat_id == payload.seat_id,
            Reservation.reserve_date == payload.reserve_date,
            Reservation.start_time == time(payload.start_hour, 0, 0),
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active])
        )
    ).first()
    if conflicts:
        raise HTTPException(status_code=409, detail="Seat already reserved")

    reservation = Reservation(
        user_id=current.id,
        room_id=payload.room_id,
        seat_id=payload.seat_id,
        reserve_date=payload.reserve_date,
        start_time=time(payload.start_hour, 0, 0),
        hours=payload.hours,
        status=ReservationStatus.pending,
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.get("/mine")
def my_reservations(
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    return session.exec(
        select(Reservation).where(Reservation.user_id == current.id).order_by(Reservation.id.desc())
    ).all()


@router.post("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if reservation.user_id != current.id:
        raise HTTPException(status_code=403, detail="Cannot cancel others reservation")
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending reservation can be canceled")

    reservation.status = ReservationStatus.canceled
    session.add(reservation)
    session.commit()
    return {"ok": True, "reservation_id": reservation_id, "status": reservation.status}


@router.get("")
def list_all_reservations(
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view"))
):
    return session.exec(select(Reservation).order_by(Reservation.id.desc())).all()
