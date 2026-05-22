from enum import Enum
from datetime import date, time, datetime

from sqlmodel import SQLModel, Field, Relationship


class ReservationStatus(str, Enum):
    pending = "pending"
    active = "active"
    canceled = "canceled"
    defaulted = "defaulted"
    finished = "finished"


class UserRoleLink(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)


class RolePermissionLink(SQLModel, table=True):
    role_id: int = Field(foreign_key="role.id", primary_key=True)
    permission_id: int = Field(foreign_key="permission.id", primary_key=True)


class User(SQLModel, table=True):
    id: str = Field(primary_key=True, max_length=25)
    name: str = Field(max_length=25)
    password_hash: str = Field(max_length=120)
    email: str = Field(max_length=100)
    credit_score: int = Field(default=100, ge=0)
    default_count: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Role(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=40)
    name: str = Field(max_length=40)


class Permission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=60)
    name: str = Field(max_length=60)


class StudyRoom(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    campus: str = Field(max_length=30)
    building: str = Field(max_length=30)
    name: str = Field(max_length=30)
    opens_at: str = Field(default="07:00")
    closes_at: str = Field(default="22:00")
    enabled: bool = Field(default=True)


class Seat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="studyroom.id")
    seat_code: str = Field(max_length=20)
    by_window: bool = Field(default=False)
    has_power: bool = Field(default=False)
    enabled: bool = Field(default=True)


class Reservation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    room_id: int = Field(foreign_key="studyroom.id")
    seat_id: int = Field(foreign_key="seat.id")
    reserve_date: date
    start_time: time
    hours: int = Field(ge=1, le=4)
    status: ReservationStatus = Field(default=ReservationStatus.pending)
    checkin_code: str | None = Field(default=None, max_length=12)


class Violation(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    reservation_id: int = Field(foreign_key="reservation.id")
    user_id: str = Field(foreign_key="user.id")
    reason: str = Field(max_length=120)
    happened_at: datetime = Field(default_factory=datetime.utcnow)


class SystemParameter(SQLModel, table=True):
    key: str = Field(primary_key=True, max_length=50)
    value: str = Field(max_length=100)
