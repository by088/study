from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.api.admin_params import router as admin_params_router
from app.api.admin_rooms import router as admin_rooms_router
from app.api.admin_reservations import router as admin_reservations_router
from app.api.admin_seats import router as admin_seats_router
from app.api.admin_users import router as admin_users_router
from app.api.auth import router as auth_router, legacy_router as auth_legacy_router
from app.api.bookings import router as booking_router
from app.api.checkin import router as checkin_router, legacy_router as checkin_legacy_router
from app.api.jobs import router as jobs_router
from app.api.rbac import router as rbac_router
from app.api.rooms import router as room_router, legacy_router as room_legacy_router
from app.api.reservations import router as reservation_router, legacy_router as reservation_legacy_router
from app.api.assistant import router as assistant_router
from app.api.stories import router as story_router
from app.core.config import settings
from app.core.db import init_db, engine
from app.core.seed import seed_base_data

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    with Session(engine) as session:
        seed_base_data(session)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": settings.app_name}


app.include_router(auth_router)
app.include_router(auth_legacy_router)
app.include_router(booking_router)
app.include_router(room_router)
app.include_router(room_legacy_router)
app.include_router(reservation_router)
app.include_router(reservation_legacy_router)
app.include_router(checkin_router)
app.include_router(checkin_legacy_router)
app.include_router(rbac_router)
app.include_router(admin_users_router)
app.include_router(admin_seats_router)
app.include_router(admin_params_router)
app.include_router(admin_rooms_router)
app.include_router(admin_reservations_router)
app.include_router(jobs_router)
app.include_router(assistant_router)
app.include_router(story_router)

