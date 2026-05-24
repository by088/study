from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.domain.rules import validate_hourly_slot

router = APIRouter(prefix="/v1/bookings", tags=["bookings"])


class BookingValidationRequest(BaseModel):
    start_at: datetime
    hours: int


@router.post("/validate")
def validate_booking(payload: BookingValidationRequest):
    try:
        validate_hourly_slot(payload.start_at, payload.hours, settings.max_reservation_hours)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "message": "Booking slot is valid."}
