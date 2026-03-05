from unittest.mock import Mock

from src.domain.exceptions import ConflictError, NotFoundError


def test_ride_start_returns_200_and_payload(client, fleet_manager_mock: Mock) -> None:
    # Mock service return: (ride, start_station_id)
    ride = Mock(ride_id=123, vehicle_id="V-7")
    fleet_manager_mock.start_ride.return_value = (ride, 10)

    # Route derives type from fleet_manager.vehicles[ride.vehicle_id]
    class Bicycle:  # class name becomes the vehicle_type
        pass

    fleet_manager_mock.vehicles = {"V-7": Bicycle()}

    resp = client.post("/ride/start", json={"user_id": 1, "lon": 34.8, "lat": 32.1})
    assert resp.status_code == 200
    assert resp.json() == {
        "ride_id": 123,
        "vehicle_id": "V-7",
        "vehicle_type": "Bicycle",
        "start_station_id": 10,
    }

    # location must be (lat, lon)
    fleet_manager_mock.start_ride.assert_called_once_with(user_id=1, location=(32.1, 34.8))


def test_ride_start_maps_not_found_to_404(client, fleet_manager_mock: Mock) -> None:
    fleet_manager_mock.start_ride.side_effect = NotFoundError("User not found")
    try:
        resp = client.post("/ride/start", json={"user_id": 999, "lon": 34.8, "lat": 32.1})
        assert resp.status_code == 404
    finally:
        fleet_manager_mock.start_ride.side_effect = None


def test_ride_start_maps_conflict_to_409(client, fleet_manager_mock: Mock) -> None:
    fleet_manager_mock.start_ride.side_effect = ConflictError("No eligible vehicles")
    try:
        resp = client.post("/ride/start", json={"user_id": 1, "lon": 34.8, "lat": 32.1})
        assert resp.status_code == 409
    finally:
        fleet_manager_mock.start_ride.side_effect = None
