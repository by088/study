from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.db import get_session
from app.domain.jobs import collect_before_15_targets, collect_after_10_targets
from app.domain.models import Reservation

router = APIRouter(prefix="/v1/jobs", tags=["jobs"])


@router.post("/notify-before-15")
def notify_before_15(session: Session = Depends(get_session)):
    now = datetime.now()
    hit = collect_before_15_targets(session, now)
    return {"ok": True, "count": len(hit), "targets": [h.user_id for h in hit]}


@router.post("/notify-after-10")
def notify_after_10(session: Session = Depends(get_session)):
    now = datetime.now()
    hit = collect_after_10_targets(session, now)
    return {"ok": True, "count": len(hit), "targets": [h.user_id for h in hit]}
