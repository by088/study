from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.domain.models import Reservation, ReservationStatus, User, Violation


def collect_before_15_targets(session: Session, now: datetime):
    pending = session.exec(select(Reservation).where(Reservation.status == ReservationStatus.pending)).all()
    hit = []
    for r in pending:
        start_dt = datetime.combine(r.reserve_date, r.start_time)
        delta = (start_dt - now).total_seconds() / 60
        if 14 <= delta <= 16:
            hit.append(r)
    return hit


def collect_after_10_targets(session: Session, now: datetime):
    pending = session.exec(select(Reservation).where(Reservation.status == ReservationStatus.pending)).all()
    hit = []
    for r in pending:
        start_dt = datetime.combine(r.reserve_date, r.start_time)
        delta = (start_dt - now).total_seconds() / 60
        if -11 <= delta <= -9:
            hit.append(r)
    return hit


def sweep_defaults(session: Session, now: datetime):
    pending = session.exec(select(Reservation).where(Reservation.status == ReservationStatus.pending)).all()
    affected = 0
    for r in pending:
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
    return affected


def sweep_finished(session: Session, now: datetime):
    active_items = session.exec(select(Reservation).where(Reservation.status == ReservationStatus.active)).all()
    affected = 0
    for r in active_items:
        end_dt = datetime.combine(r.reserve_date, r.start_time) + timedelta(hours=r.hours)
        if now >= end_dt:
            r.status = ReservationStatus.finished
            session.add(r)
            affected += 1
    session.commit()
    return affected
