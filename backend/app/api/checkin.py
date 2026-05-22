from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, User, Violation

router = APIRouter(prefix="/v1/checkin", tags=["checkin"])


class CheckinRequest(BaseModel):
    reservation_id: int
    code: str


@router.post("")
def checkin(
    payload: CheckinRequest,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    rsv = session.get(Reservation, payload.reservation_id)
    if not rsv or rsv.user_id != current.id:
        raise HTTPException(status_code=404, detail="Reservation not found")
    if rsv.status != ReservationStatus.pending:
        raise HTTPException(status_code=400, detail="Reservation is not pending")

    expected = rsv.checkin_code or "0000"
    if payload.code != expected:
        raise HTTPException(status_code=400, detail="Invalid check-in code")

    rsv.status = ReservationStatus.active
    session.add(rsv)
    session.commit()
    return {"ok": True, "reservation_id": rsv.id, "status": rsv.status}


@router.post("/sweep-defaults")
def sweep_defaults(session: Session = Depends(get_session)):
    # stage2 first-pass: convert pending to default if start+15min passed on same day
    now = datetime.now()
    pending_items = session.exec(select(Reservation).where(Reservation.status == ReservationStatus.pending)).all()
    affected = 0

    for r in pending_items:
        start_dt = datetime.combine(r.reserve_date, r.start_time)
        if now >= start_dt + timedelta(minutes=15):
            r.status = ReservationStatus.defaulted
            user = session.get(User, r.user_id)
            if user:
                user.default_count += 1
                user.credit_score = max(0, user.credit_score - 10)
                session.add(user)
            session.add(r)
            session.add(Violation(reservation_id=r.id, user_id=r.user_id, reason="No check-in after 15 minutes"))
            affected += 1

    session.commit()
    return {"ok": True, "affected": affected}
