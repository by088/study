from fastapi import FastAPI
from sqlmodel import Session

from app.api.admin_params import router as admin_params_router
from app.api.admin_reservations import router as admin_reservations_router
from app.api.admin_seats import router as admin_seats_router
from app.api.admin_users import router as admin_users_router
from app.api.auth import router as auth_router
from app.api.bookings import router as booking_router
from app.api.checkin import router as checkin_router
from app.api.jobs import router as jobs_router
from app.api.rbac import router as rbac_router
from app.api.rooms import router as room_router
from app.api.reservations import router as reservation_router
from app.api.stories import router as story_router
from app.core.config import settings
from app.core.db import init_db, engine
from app.core.seed import seed_base_data

app = FastAPI(title=settings.app_name)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with Session(engine) as session:
        seed_base_data(session)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router)
app.include_router(booking_router)
app.include_router(room_router)
app.include_router(reservation_router)
app.include_router(checkin_router)
app.include_router(rbac_router)
app.include_router(admin_users_router)
app.include_router(admin_seats_router)
app.include_router(admin_params_router)
app.include_router(admin_reservations_router)
app.include_router(jobs_router)
app.include_router(story_router)
