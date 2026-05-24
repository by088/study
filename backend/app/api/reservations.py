from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user, require_permission
from app.core.config import settings
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, Seat, StudyRoom, User
from app.domain.rules import validate_hourly_slot

router = APIRouter(prefix="/v1/reservations", tags=["reservations"])
legacy_router = APIRouter(tags=["reservations-legacy"])


class ReservationCreateRequest(BaseModel):
    room_id: int
    seat_id: int
    reserve_date: date
    start_hour: int
    hours: int


class LegacyBookingRequest(BaseModel):
    room_id: int
    seat_number: str
    reservation_time: int
    reservation_hours: int


def _hour_window_conflict(a_start: datetime, a_hours: int, b_start: datetime, b_hours: int) -> bool:
    a_end = a_start + timedelta(hours=a_hours)
    b_end = b_start + timedelta(hours=b_hours)
    return max(a_start, b_start) < min(a_end, b_end)


def _legacy_status(status: ReservationStatus) -> str:
    mapping = {
        ReservationStatus.pending: "0",
        ReservationStatus.active: "1",
        ReservationStatus.canceled: "2",
        ReservationStatus.defaulted: "3",
        ReservationStatus.finished: "4",
    }
    return mapping[status]


@router.post("")
def create_reservation(
    payload: ReservationCreateRequest,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    if current.credit_score < settings.min_credit_score:
        raise HTTPException(status_code=400, detail="Credit score too low")

    start_at = datetime.combine(payload.reserve_date, time(payload.start_hour, 0, 0))
    try:
        validate_hourly_slot(start_at, payload.hours, settings.max_reservation_hours)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    room = session.get(StudyRoom, payload.room_id)
    if not room or not room.enabled:
        raise HTTPException(status_code=404, detail="Room not found")

    if not room.open_to_all and room.department:
        if current.department != room.department:
            raise HTTPException(status_code=403, detail=f"该自习室仅对 {room.department} 院系学生开放")

    seat = session.get(Seat, payload.seat_id)
    if not seat or seat.room_id != payload.room_id or not seat.enabled:
        raise HTTPException(status_code=404, detail="Seat not found")

    same_day_active = session.exec(
        select(Reservation).where(
            Reservation.user_id == current.id,
            Reservation.reserve_date == payload.reserve_date,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()
    for existing in same_day_active:
        e_start = datetime.combine(existing.reserve_date, existing.start_time)
        if _hour_window_conflict(start_at, payload.hours, e_start, existing.hours):
            raise HTTPException(status_code=400, detail="Time conflict with your existing reservation")

    conflicts = session.exec(
        select(Reservation).where(
            Reservation.seat_id == payload.seat_id,
            Reservation.reserve_date == payload.reserve_date,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()
    for r in conflicts:
        r_start = datetime.combine(r.reserve_date, r.start_time)
        if _hour_window_conflict(start_at, payload.hours, r_start, r.hours):
            raise HTTPException(status_code=409, detail="Seat already reserved")

    reservation = Reservation(
        user_id=current.id,
        room_id=payload.room_id,
        seat_id=payload.seat_id,
        reserve_date=payload.reserve_date,
        start_time=time(payload.start_hour, 0, 0),
        hours=payload.hours,
        status=ReservationStatus.pending,
        checkin_code="0000",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation


@router.get("/mine")
def my_reservations(session: Session = Depends(get_session), current: User = Depends(get_current_user)):
    return session.exec(select(Reservation).where(Reservation.user_id == current.id).order_by(Reservation.id.desc())).all()


@router.post("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
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
    _: User = Depends(require_permission("reservation.view")),
):
    return session.exec(select(Reservation).order_by(Reservation.id.desc())).all()


@legacy_router.post("/v1/studyroom/booking")
def legacy_booking(
    payload: LegacyBookingRequest,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    if current.credit_score < settings.min_credit_score:
        return {"success": False, "code": 401}

    room = session.get(StudyRoom, payload.room_id)
    if not room or not room.enabled:
        return {"success": False, "code": 400}

    if not room.open_to_all and room.department:
        if current.department != room.department:
            return {"success": False, "code": 407, "message": f"该自习室仅对 {room.department} 院系学生开放"}

    start_dt = datetime.combine(date.today(), time(payload.reservation_time, 0, 0))
    try:
        validate_hourly_slot(start_dt, payload.reservation_hours, settings.max_reservation_hours)
    except ValueError:
        return {"success": False, "code": 403}

    opens = int(room.opens_at.split(":")[0])
    closes = int(room.closes_at.split(":")[0])
    if not (opens <= payload.reservation_time < closes):
        return {"success": False, "code": 406}
    if payload.reservation_time + payload.reservation_hours > closes:
        return {"success": False, "code": 403}

    user_reservations = session.exec(
        select(Reservation).where(
            Reservation.user_id == current.id,
            Reservation.reserve_date == date.today(),
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()
    for ur in user_reservations:
        ur_start = datetime.combine(ur.reserve_date, ur.start_time)
        if _hour_window_conflict(start_dt, payload.reservation_hours, ur_start, ur.hours):
            return {"success": False, "code": 405, "message": "你在该时间段已有预约，时间冲突"}

    seat = session.exec(
        select(Seat).where(
            Seat.room_id == payload.room_id,
            Seat.enabled == True,
        )
    ).all()
    seat = next(
        (
            s
            for s in seat
            if s.seat_code == str(payload.seat_number)
            or s.seat_code.endswith(f"-{payload.seat_number}")
        ),
        None,
    )
    if not seat:
        return {"success": False, "code": 400}

    seat_reservations = session.exec(
        select(Reservation).where(
            Reservation.seat_id == seat.id,
            Reservation.reserve_date == date.today(),
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()
    for r in seat_reservations:
        r_start = datetime.combine(r.reserve_date, r.start_time)
        if _hour_window_conflict(start_dt, payload.reservation_hours, r_start, r.hours):
            return {"success": False, "code": 402}

    reservation = Reservation(
        user_id=current.id,
        room_id=payload.room_id,
        seat_id=seat.id,
        reserve_date=date.today(),
        start_time=time(payload.reservation_time, 0, 0),
        hours=payload.reservation_hours,
        status=ReservationStatus.pending,
        checkin_code="0000",
    )
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return {"success": True, "code": 100, "reservation_id": reservation.id}


@legacy_router.get("/v1/reservations/info")
def legacy_reservations_info(session: Session = Depends(get_session), current: User = Depends(get_current_user)):
    reservations = session.exec(
        select(Reservation).where(Reservation.user_id == current.id).order_by(Reservation.id.desc())
    ).all()
    data = []
    for r in reservations:
        room = session.get(StudyRoom, r.room_id)
        seat = session.get(Seat, r.seat_id)
        data.append(
            {
                "reservation_id": r.id,
                "date": str(r.reserve_date),
                "reservation_time": r.start_time.strftime("%H:%M:%S"),
                "reservation_hours": r.hours,
                "reservation_status": _legacy_status(r.status),
                "room_name": room.name if room else "",
                "room_id": r.room_id,
                "seat_number": seat.seat_code if seat else "",
                "campus_name": room.campus if room else "",
                "building_name": room.building if room else "",
            }
        )
    return {"success": True, "code": 100, "data": data}


@legacy_router.get("/v1/reservations/invalid")
def legacy_reservations_invalid(session: Session = Depends(get_session), current: User = Depends(get_current_user)):
    r = session.exec(
        select(Reservation).where(Reservation.user_id == current.id, Reservation.status == ReservationStatus.pending).order_by(Reservation.id.desc())
    ).first()
    if not r:
        return {"success": False, "code": 400, "data": "empty"}
    room = session.get(StudyRoom, r.room_id)
    seat = session.get(Seat, r.seat_id)
    return {
        "success": True,
        "code": 100,
        "data": {
            "reservation_id": r.id,
            "date": str(r.reserve_date),
            "reservation_time": r.start_time.strftime("%H:%M:%S"),
            "reservation_hours": r.hours,
            "reservation_status": _legacy_status(r.status),
            "room_name": room.name if room else "",
            "room_id": r.room_id,
            "seat_number": seat.seat_code if seat else "",
            "campus_name": room.campus if room else "",
            "building_name": room.building if room else "",
        },
    }


@legacy_router.put("/v1/reservations/cancel")
def legacy_cancel(
    reservation_id: int,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    reservation = session.get(Reservation, reservation_id)
    if not reservation or reservation.user_id != current.id:
        return {"success": False, "code": 700}
    if reservation.status == ReservationStatus.active:
        return {"success": False, "code": 701}
    if reservation.status == ReservationStatus.canceled:
        return {"success": False, "code": 702}
    if reservation.status == ReservationStatus.defaulted:
        return {"success": False, "code": 703}
    if reservation.status == ReservationStatus.finished:
        return {"success": False, "code": 704}

    reservation.status = ReservationStatus.canceled
    session.add(reservation)
    session.commit()
    return {"success": True, "code": 100}
