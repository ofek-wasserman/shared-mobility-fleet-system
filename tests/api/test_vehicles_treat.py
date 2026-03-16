from unittest.mock import Mock

from fastapi.testclient import TestClient

from src.domain.exceptions import ConflictError, NotFoundError


def test_treat_vehicle_returns_treated_vehicle_ids(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.apply_treatment.return_value = ["V001", "V007"]

    resp = client.post(
        "/vehicle/treat",
        json={"lat": 32.1, "lon": 34.8},
    )

    assert resp.status_code == 200
    assert resp.json() == {"treated_vehicle_ids": ["V001", "V007"]}
    fleet_manager_mock.apply_treatment.assert_called_once_with((32.1, 34.8))


def test_treat_vehicle_returns_empty_list(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.apply_treatment.return_value = []

    resp = client.post(
        "/vehicle/treat",
        json={"lat": 32.1, "lon": 34.8},
    )

    assert resp.status_code == 200
    assert resp.json() == {"treated_vehicle_ids": []}
    fleet_manager_mock.apply_treatment.assert_called_once_with((32.1, 34.8))


def test_treat_vehicle_invalid_input_returns_400(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    resp = client.post(
        "/vehicle/treat",
        json={"lat": "32.1", "lon": 34.8},
    )

    assert resp.status_code == 400


def test_treat_vehicle_missing_entity_returns_404(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.apply_treatment.side_effect = NotFoundError("Vehicle V001 not found.")

    resp = client.post(
        "/vehicle/treat",
        json={"lat": 32.1, "lon": 34.8},
    )

    assert resp.status_code == 404
    assert resp.json() == {"detail": "Vehicle V001 not found."}


def test_treat_vehicle_conflicting_state_returns_409(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.apply_treatment.side_effect = ConflictError(
        "No station with free slot available"
    )

    resp = client.post(
        "/vehicle/treat",
        json={"lat": 32.1, "lon": 34.8},
    )

    assert resp.status_code == 409
    assert resp.json() == {"detail": "No station with free slot available"}
