from unittest.mock import Mock, patch

from src.domain.exceptions import ConflictError, NotFoundError


def test_ride_start_returns_200_and_payload(client, fleet_manager_mock: Mock) -> None:
    ride = Mock(ride_id=123, vehicle_id="V-7")
    fleet_manager_mock.start_ride.return_value = (ride, 10)

    class Bicycle:
        pass

    fleet_manager_mock.vehicles = {"V-7": Bicycle()}

    with patch("src.api.routes.rides.save_state") as save_state_mock:
        resp = client.post("/ride/start", json={"user_id": 1, "lon": 34.8, "lat": 32.1})

    assert resp.status_code == 200
    assert resp.json() == {
        "ride_id": 123,
        "vehicle_id": "V-7",
        "vehicle_type": "Bicycle",
        "start_station_id": 10,
    }

    fleet_manager_mock.start_ride.assert_called_once_with(user_id=1, location=(32.1, 34.8))
    save_state_mock.assert_called_once()


def test_ride_start_maps_not_found_to_404(client, fleet_manager_mock: Mock) -> None:
    fleet_manager_mock.start_ride.side_effect = NotFoundError("User not found")
    try:
        with patch("src.api.routes.rides.save_state") as save_state_mock:
            resp = client.post("/ride/start", json={"user_id": 999, "lon": 34.8, "lat": 32.1})

        assert resp.status_code == 404
        save_state_mock.assert_not_called()
    finally:
        fleet_manager_mock.start_ride.side_effect = None


def test_ride_start_maps_conflict_to_409(client, fleet_manager_mock: Mock) -> None:
    fleet_manager_mock.start_ride.side_effect = ConflictError("No eligible vehicles")
    try:
        with patch("src.api.routes.rides.save_state") as save_state_mock:
            resp = client.post("/ride/start", json={"user_id": 1, "lon": 34.8, "lat": 32.1})

        assert resp.status_code == 409
        save_state_mock.assert_not_called()
    finally:
        fleet_manager_mock.start_ride.side_effect = None
