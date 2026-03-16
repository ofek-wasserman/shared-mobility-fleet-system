from unittest.mock import Mock, patch

from starlette.testclient import TestClient

from src.domain.exceptions import ConflictError


def test_register_returns_201_and_user_id(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    with patch("src.api.routes.users.save_state") as save_state_mock:
        resp = client.post("/register", json={"payment_token": "tok_123"})

    assert resp.status_code == 201
    body = resp.json()
    assert "user_id" in body
    assert isinstance(body["user_id"], int)

    fleet_manager_mock.register_user.assert_called_once_with("tok_123")
    save_state_mock.assert_called_once()


def test_register_strict_types_rejects_non_string_token(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    with patch("src.api.routes.users.save_state") as save_state_mock:
        resp = client.post("/register", json={"payment_token": 123})

    assert resp.status_code == 400
    fleet_manager_mock.register_user.assert_not_called()
    save_state_mock.assert_not_called()


def test_register_extra_fields_forbidden(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    with patch("src.api.routes.users.save_state") as save_state_mock:
        resp = client.post("/register", json={"payment_token": "tok", "extra": "nope"})

    assert resp.status_code == 400
    fleet_manager_mock.register_user.assert_not_called()
    save_state_mock.assert_not_called()


def test_register_missing_payment_token_returns_400(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    with patch("src.api.routes.users.save_state") as save_state_mock:
        resp = client.post("/register", json={})

    assert resp.status_code == 400
    fleet_manager_mock.register_user.assert_not_called()
    save_state_mock.assert_not_called()


def test_register_duplicate_token_returns_409(
    client: TestClient,
    fleet_manager_mock: Mock,
) -> None:
    fleet_manager_mock.register_user.side_effect = [
        1,
        ConflictError("Payment token already registered."),
    ]

    try:
        with patch("src.api.routes.users.save_state") as save_state_mock:
            r1 = client.post("/register", json={"payment_token": "dup"})
            assert r1.status_code == 201

            r2 = client.post("/register", json={"payment_token": "dup"})
            assert r2.status_code == 409

        assert save_state_mock.call_count == 1
    finally:
        fleet_manager_mock.register_user.side_effect = None
