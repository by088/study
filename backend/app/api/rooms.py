from datetime import date, datetime, time, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import get_current_user, require_permission
from app.core.db import get_session
from app.domain.models import Reservation, ReservationStatus, StudyRoom, Seat, User

router = APIRouter(prefix="/v1/rooms", tags=["rooms"])


class RoomCreateRequest(BaseModel):
    campus: str
    building: str
    name: str
    opens_at: str = "07:00"
    closes_at: str = "22:00"


@router.get("")
def list_rooms(
    campus: Optional[str] = None,
    has_power: Optional[bool] = None,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user)
):
    stmt = select(StudyRoom).where(StudyRoom.enabled == True)
    if campus:
        stmt = stmt.where(StudyRoom.campus == campus)
    rooms = session.exec(stmt).all()

    # 过滤院系限制：非全校开放的自习室仅展示给本院系学生
    rooms = [
        r for r in rooms
        if r.open_to_all or not r.department or r.department == current.department
    ]

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
    room = StudyRoom(**payload.dict())
    session.add(room)
    session.commit()
    session.refresh(room)
    return room


@router.get("/{room_id}/seats")
def list_room_seats(
    room_id: int,
    by_window: Optional[bool] = None,
    has_power: Optional[bool] = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user)
):
    stmt = select(Seat).where(Seat.room_id == room_id, Seat.enabled == True)
    if by_window is not None:
        stmt = stmt.where(Seat.by_window == by_window)
    if has_power is not None:
        stmt = stmt.where(Seat.has_power == has_power)
    return session.exec(stmt).all()


def _status_char(hours_available: int, has_power: bool) -> str:
    base = "ABCDE" if has_power else "abcde"
    if hours_available <= 0:
        return base[0]
    if hours_available == 1:
        return base[1]
    if hours_available == 2:
        return base[2]
    if hours_available == 3:
        return base[3]
    return base[4]


def _seat_availability(
    session: Session,
    seat: Seat,
    target_date: date,
    start_hour: int,
    room_close_hour: int,
) -> int:
    start_dt = datetime.combine(target_date, time(start_hour, 0, 0))
    max_hours = room_close_hour - start_hour
    if max_hours <= 0:
        return 0
    reservations = session.exec(
        select(Reservation).where(
            Reservation.seat_id == seat.id,
            Reservation.reserve_date == target_date,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.active]),
        )
    ).all()
    best = max_hours
    for r in reservations:
        r_start = datetime.combine(target_date, r.start_time)
        r_end = r_start + timedelta(hours=r.hours)
        if r_start <= start_dt < r_end:
            return 0
        if r_start > start_dt:
            gap = int((r_start - start_dt).total_seconds() // 3600)
            best = min(best, gap)
    return max(0, min(4, best))


legacy_router = APIRouter(tags=["rooms-legacy"])


@legacy_router.get("/v1/campus")
def legacy_campus(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    rows = session.exec(select(StudyRoom.campus).where(StudyRoom.enabled == True).distinct()).all()
    return {"success": True, "code": 100, "data": [{"campus_id": c, "campus_name": c} for c in rows]}


@legacy_router.get("/v1/building")
def legacy_building(
    campus_id: Optional[str] = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    stmt = select(StudyRoom.building, StudyRoom.campus).where(StudyRoom.enabled == True)
    if campus_id:
        stmt = stmt.where(StudyRoom.campus == campus_id)
    rows = session.exec(stmt.distinct()).all()
    data = [{"building_id": b, "building_name": b, "campus_id": c} for b, c in rows]
    return {"success": True, "code": 100, "data": data}


@legacy_router.get("/v1/studyroom")
def legacy_studyroom(
    campus_id: Optional[str] = None,
    building_id: Optional[str] = None,
    room_name: Optional[str] = None,
    have_charge: Optional[bool] = None,
    is_available: Optional[bool] = None,
    session: Session = Depends(get_session),
    current: User = Depends(get_current_user),
):
    stmt = select(StudyRoom).where(StudyRoom.enabled == True)
    if campus_id:
        stmt = stmt.where(StudyRoom.campus == campus_id)
    if building_id:
        stmt = stmt.where(StudyRoom.building == building_id)
    if room_name:
        stmt = stmt.where(StudyRoom.name.contains(room_name))
    if is_available is not None:
        stmt = stmt.where(StudyRoom.enabled == is_available)
    rooms = session.exec(stmt).all()
    # 过滤院系限制
    rooms = [
        r for r in rooms
        if r.open_to_all or not r.department or r.department == current.department
    ]
    data = []
    for room in rooms:
        seats = session.exec(select(Seat).where(Seat.room_id == room.id, Seat.enabled == True)).all()
        charge_count = len([s for s in seats if s.has_power])
        if have_charge is True and charge_count == 0:
            continue
        data.append(
            {
                "room_id": room.id,
                "campus_id": room.campus,
                "building_id": room.building,
                "room_name": room.name,
                "number_of_seats": len(seats),
                "is_available": room.enabled,
                "open_time": room.opens_at,
                "close_time": room.closes_at,
                "have_charge": charge_count,
                "department": room.department,
                "open_to_all": room.open_to_all,
            }
        )
    return {"success": True, "code": 100, "data": data}


@legacy_router.get("/v1/studyroom/seatstatus")
def legacy_seatstatus(
    room_id: int,
    time_start: int,
    reserve_date: Optional[date] = None,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    room = session.get(StudyRoom, room_id)
    if not room:
        return {"success": False, "code": 400, "data": "room not found"}
    seats = session.exec(
        select(Seat).where(Seat.room_id == room_id, Seat.enabled == True).order_by(Seat.seat_code)
    ).all()
    close_hour = int(room.closes_at.split(":")[0])
    target_date = reserve_date or date.today()
    chars = []
    for seat in seats:
        av = _seat_availability(session, seat, target_date, time_start, close_hour)
        chars.append(_status_char(av, seat.has_power))
    return {"success": True, "code": 100, "data": "".join(chars)}

