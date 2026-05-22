from datetime import date

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_auth_and_reservation_flow():
    register_payload = {
        "user_id": "autotest-stu",
        "name": "Auto Test",
        "password": "Pass1234",
        "email": "autotest@example.com"
    }
    client.post("/v1/auth/register", json=register_payload)

    login_resp = client.post("/v1/auth/login", json={"user_id": "autotest-stu", "password": "Pass1234"})
    assert login_resp.status_code == 200
    token = login_resp.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    rooms_resp = client.get("/v1/rooms", headers=headers)
    assert rooms_resp.status_code == 200
    rooms = rooms_resp.json()
    assert len(rooms) >= 1

    room_id = rooms[0]["id"]
    seats_resp = client.get(f"/v1/rooms/{room_id}/seats", headers=headers)
    assert seats_resp.status_code == 200
    seats = seats_resp.json()
    assert len(seats) >= 1

    reservation_resp = client.post(
        "/v1/reservations",
        headers=headers,
        json={
            "room_id": room_id,
            "seat_id": seats[0]["id"],
            "reserve_date": str(date.today()),
            "start_hour": 20,
            "hours": 2,
        },
    )
    assert reservation_resp.status_code in [200, 409]
