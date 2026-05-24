from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_with_wrong_password_should_fail():
    client.post(
        "/v1/auth/register",
        json={"user_id": "neg-user", "name": "Neg", "password": "Pass1234", "email": "neg@example.com"},
    )
    resp = client.post("/v1/auth/login", json={"user_id": "neg-user", "password": "bad-pass"})
    assert resp.status_code == 401


def test_validate_slot_reject_non_hour():
    resp = client.post("/v1/bookings/validate", json={"start_at": "2026-05-23T10:30:00", "hours": 2})
    assert resp.status_code == 400
