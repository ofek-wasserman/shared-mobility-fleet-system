from pathlib import Path

from fastapi.testclient import TestClient

from src.main import create_app


def make_client(tmp_path: Path) -> TestClient:
    app = create_app()
    app.state.state_path = tmp_path / "state.json"
    return TestClient(app)


def test_register_user_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resp = client.post("/register", json={"payment_token": "token_e2e_1"})

        assert resp.status_code == 201
        body = resp.json()
        assert "user_id" in body
        assert isinstance(body["user_id"], int)


def test_start_and_end_ride_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        register_resp = client.post("/register", json={"payment_token": "token_e2e_2"})
        assert register_resp.status_code == 201
        register_body = register_resp.json()
        assert "user_id" in register_body
        assert isinstance(register_body["user_id"], int)
        user_id = register_body["user_id"]

        start_resp = client.post(
            "/ride/start",
            json={"user_id": user_id, "lat": 32.0853, "lon": 34.7818},
        )
        assert start_resp.status_code == 200
        start_body = start_resp.json()
        assert "ride_id" in start_body
        assert "vehicle_id" in start_body
        assert "vehicle_type" in start_body
        assert "start_station_id" in start_body
        assert isinstance(start_body["ride_id"], int)
        assert isinstance(start_body["vehicle_id"], str)
        assert isinstance(start_body["vehicle_type"], str)
        assert isinstance(start_body["start_station_id"], int)
        ride_id = start_body["ride_id"]

        end_resp = client.post(
            "/ride/end",
            json={"ride_id": ride_id, "lat": 32.0853, "lon": 34.7818},
        )
        assert end_resp.status_code == 200
        end_body = end_resp.json()
        assert end_body["ride_id"] == ride_id
        assert isinstance(end_body["end_station_id"], int)
        assert isinstance(end_body["payment_charged"], (int, float))


def test_nearest_station_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resp = client.get("/stations/nearest?lat=32.0853&lon=34.7818")

        assert resp.status_code == 200
        body = resp.json()
        assert "station_id" in body
        assert "lat" in body
        assert "lon" in body
        assert isinstance(body["station_id"], int)
        assert isinstance(body["lat"], float)
        assert isinstance(body["lon"], float)


def test_active_users_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        before_resp = client.get("/rides/active-users")
        assert before_resp.status_code == 200
        before_body = before_resp.json()
        assert "active_user_ids" in before_body
        assert isinstance(before_body["active_user_ids"], list)

        register_resp = client.post("/register", json={"payment_token": "token_e2e_3"})
        assert register_resp.status_code == 201
        register_body = register_resp.json()
        assert "user_id" in register_body
        assert isinstance(register_body["user_id"], int)
        user_id = register_body["user_id"]

        start_resp = client.post(
            "/ride/start",
            json={"user_id": user_id, "lat": 32.0853, "lon": 34.7818},
        )
        assert start_resp.status_code == 200

        active_resp = client.get("/rides/active-users")
        assert active_resp.status_code == 200
        active_body = active_resp.json()
        assert "active_user_ids" in active_body
        assert isinstance(active_body["active_user_ids"], list)
        assert user_id in active_body["active_user_ids"]


def test_report_vehicle_degraded_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        register_resp = client.post("/register", json={"payment_token": "token_e2e_4"})
        assert register_resp.status_code == 201
        register_body = register_resp.json()
        assert "user_id" in register_body
        assert isinstance(register_body["user_id"], int)
        user_id = register_body["user_id"]

        start_resp = client.post(
            "/ride/start",
            json={"user_id": user_id, "lat": 32.0853, "lon": 34.7818},
        )
        assert start_resp.status_code == 200
        start_body = start_resp.json()
        assert "vehicle_id" in start_body
        assert isinstance(start_body["vehicle_id"], str)
        vehicle_id = start_body["vehicle_id"]

        resp = client.post(
            "/vehicle/report-degraded",
            json={"user_id": user_id, "vehicle_id": vehicle_id},
        )

        assert resp.status_code == 200
        assert resp.json() == {"result": "ok"}


def test_vehicle_treat_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resp = client.post(
            "/vehicle/treat",
            json={"lat": 32.0853, "lon": 34.7818},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert "treated_vehicle_ids" in body
        assert isinstance(body["treated_vehicle_ids"], list)
        assert all(isinstance(vehicle_id, str) for vehicle_id in body["treated_vehicle_ids"])


def test_register_duplicate_token_returns_409_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        r1 = client.post("/register", json={"payment_token": "dup_token"})
        assert r1.status_code == 201

        r2 = client.post("/register", json={"payment_token": "dup_token"})
        assert r2.status_code == 409


def test_invalid_register_body_returns_400_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resp = client.post("/register", json={"payment_token": 123})

        assert resp.status_code == 400


def test_report_degraded_missing_vehicle_returns_404_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        register_resp = client.post("/register", json={"payment_token": "token_e2e_5"})
        assert register_resp.status_code == 201
        register_body = register_resp.json()
        assert "user_id" in register_body
        assert isinstance(register_body["user_id"], int)
        user_id = register_body["user_id"]

        resp = client.post(
            "/vehicle/report-degraded",
            json={"user_id": user_id, "vehicle_id": "MISSING"},
        )

        assert resp.status_code == 404


def test_start_ride_missing_user_returns_404_e2e(tmp_path: Path) -> None:
    with make_client(tmp_path) as client:
        resp = client.post(
            "/ride/start",
            json={"user_id": 999999, "lat": 32.0853, "lon": 34.7818},
        )

        assert resp.status_code == 404
