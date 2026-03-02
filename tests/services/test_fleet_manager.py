"""Tests for FleetManager (orchestration skeleton + DI + in-memory state)."""

from unittest.mock import MagicMock

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
