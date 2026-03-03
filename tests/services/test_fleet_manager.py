"""Tests for FleetManager (orchestration skeleton + DI + in-memory state)."""

from unittest.mock import MagicMock

import pytest

from src.domain.VehicleContainer import DegradedRepo
from src.services.active_rides import ActiveRidesRegistry
from src.services.billing import BillingService
from src.services.fleet_manager import FleetManager


class TestFleetManager:
    def test_initial_state(self):
        stations = {1: MagicMock(), 2: MagicMock()}
        vehicles = {10: MagicMock(), 11: MagicMock()}

        fm = FleetManager(stations=stations, vehicles=vehicles)

        assert fm.stations is stations
        assert fm.vehicles is vehicles
        assert fm.users == {}

    def test_uses_injected_dependencies(self):
        stations = {1: MagicMock()}
        vehicles = {10: MagicMock()}

        active = ActiveRidesRegistry()
        repo = DegradedRepo(container_id=-1,_vehicle_ids=set(),name="Degraded Repo")
        billing = BillingService()

        fm = FleetManager(
            stations=stations,
            vehicles=vehicles,
            active_rides=active,
            degraded_repo=repo,
            billing_service=billing,
        )

        assert fm.active_rides is active
        assert fm.degraded_repo is repo
        assert fm.billing_service is billing

    def test_default_dependencies_are_not_shared_between_instances(self):
        stations = {1: MagicMock()}
        vehicles = {10: MagicMock()}

        fm1 = FleetManager(stations=stations, vehicles=vehicles)
        fm2 = FleetManager(stations=stations, vehicles=vehicles)

        # Proves you avoided the "mutable default args" trap
        assert fm1.active_rides is not fm2.active_rides
        assert fm1.degraded_repo is not fm2.degraded_repo
        assert fm1.billing_service is not fm2.billing_service

    def test_register_user_creates_and_stores_user_and_returns_id(self):
        fm = FleetManager(stations={}, vehicles={})

        user_id = fm.register_user("tok_test")

        assert isinstance(user_id, int)
        assert user_id in fm.users
        assert fm.users[user_id].user_id == user_id
        assert fm.users[user_id].payment_token == "tok_test"

    def test_register_user_rejects_duplicate_payment_token(self):
        fm = FleetManager(stations={}, vehicles={})
        fm.register_user("tok_test")

        with pytest.raises(ValueError):
            fm.register_user("tok_test")

    def test_invalid_payment_token_raises_error(self):
        fm = FleetManager(stations={}, vehicles={})
        with pytest.raises(ValueError):
            fm.register_user("")
        with pytest.raises(ValueError):
            fm.register_user(None)
        fm.register_user("test")
        with pytest.raises(ValueError):
            fm.register_user("test ")

