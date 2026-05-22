from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import require_permission
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, User, Violation

router = APIRouter(prefix="/v1/admin/reservations", tags=["admin-reservations"])


@router.get("")
def list_reservations(
    user_id: str | None = None,
    room_id: int | None = None,
    reserve_date: date | None = None,
    status: ReservationStatus | None = None,
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
    user_id: str | None = None,
    session: Session = Depends(get_session),
    _: User = Depends(require_permission("reservation.view"))
):
    stmt = select(Violation).order_by(Violation.happened_at.desc())
    if user_id:
        stmt = stmt.where(Violation.user_id == user_id)
    return session.exec(stmt).all()
