from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from src.domain.exceptions import ConflictError, NotFoundError


def test_report_vehicle_degraded_returns_ok(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.report_degraded.return_value = None

    with patch("src.api.routes.vehicles.save_state") as save_state_mock:
        resp = client.post(
            "/vehicle/report-degraded",
            json={"user_id": 1, "vehicle_id": "V001"},
        )

    assert resp.status_code == 200
    assert resp.json() == {"result": "ok"}
    save_state_mock.assert_called_once()


def test_report_vehicle_degraded_invalid_input_returns_400(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    with patch("src.api.routes.vehicles.save_state") as save_state_mock:
        resp = client.post(
            "/vehicle/report-degraded",
            json={"user_id": "1", "vehicle_id": "V001"},
        )

    assert resp.status_code == 400
    save_state_mock.assert_not_called()


def test_report_vehicle_degraded_missing_entity_returns_404(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.report_degraded.side_effect = NotFoundError("Vehicle not found")
    try:
        with patch("src.api.routes.vehicles.save_state") as save_state_mock:
            resp = client.post(
                "/vehicle/report-degraded",
                json={"user_id": 1, "vehicle_id": "MISSING"},
            )

        assert resp.status_code == 404
        assert resp.json() == {"detail": "Vehicle not found"}
        save_state_mock.assert_not_called()
    finally:
        fleet_manager_mock.report_degraded.side_effect = None


def test_report_vehicle_degraded_conflicting_state_returns_409(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.report_degraded.side_effect = ConflictError("Vehicle already degraded")
    try:
        with patch("src.api.routes.vehicles.save_state") as save_state_mock:
            resp = client.post(
                "/vehicle/report-degraded",
                json={"user_id": 1, "vehicle_id": "V001"},
            )

        assert resp.status_code == 409
        assert resp.json() == {"detail": "Vehicle already degraded"}
        save_state_mock.assert_not_called()
    finally:
        fleet_manager_mock.report_degraded.side_effect = None
