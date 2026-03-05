"""Tests for FleetManager (orchestration skeleton + DI + in-memory state)."""

import datetime
from unittest.mock import MagicMock

import pytest

from src.domain.exceptions import ConflictError, InvalidInputError, NotFoundError
from src.domain.VehicleContainer import DegradedRepo
from src.services.active_rides import ActiveRidesRegistry
from src.services.billing import BillingService
from src.services.fleet_manager import FleetManager


class TestFleetManager:
    #-----------------------------
    # Initialization Tests
    #-----------------------------
    def test_initial_state(self):
        stations = {1: MagicMock(), 2: MagicMock()}
        vehicles = {}

        fm = FleetManager(stations=stations, vehicles=vehicles)

        assert fm.stations is stations
        assert fm.vehicles is vehicles
        assert fm.users == {}

    def test_initialize_state_eligible_vehicle_stays_in_station(self):
        station = MagicMock()
        station.remove_vehicle = MagicMock()

        stations = {1: station}

        vehicle = MagicMock()
        vehicle.is_eligible.return_value = True
        vehicle.station_id = 1
        vehicle.active_ride_id = None
        vehicle.mark_degraded = MagicMock()

        vehicles = {"V101": vehicle}

        degraded_repo = MagicMock()
        degraded_repo.add_vehicle = MagicMock()

        FleetManager(stations=stations, vehicles=vehicles, degraded_repo=degraded_repo)

        degraded_repo.add_vehicle.assert_not_called()
        vehicle.mark_degraded.assert_not_called()
        station.remove_vehicle.assert_not_called()
        station.add_vehicle.assert_called_once_with("V101")

    def test_initialize_state_ineligible_vehicle_moved_and_removed(self):
        station = MagicMock()
        station.remove_vehicle = MagicMock()

        stations = {1: station}

        vehicle = MagicMock()
        vehicle.is_eligible.return_value = False
        vehicle.station_id = 1
        vehicle.active_ride_id = None
        vehicle.mark_degraded = MagicMock()

        vehicles = {"V202": vehicle}

        degraded_repo = MagicMock()
        degraded_repo.add_vehicle = MagicMock()

        FleetManager(stations=stations, vehicles=vehicles, degraded_repo=degraded_repo)

        degraded_repo.add_vehicle.assert_called_once_with("V202")
        vehicle.mark_degraded.assert_called_once()

    def test_initialize_state_ineligible_vehicle_missing_station(self):
        # station_id points to a station that doesn't exist -> should not crash
        stations = {}

        vehicle = MagicMock()
        vehicle.is_eligible.return_value = False
        vehicle.station_id = 99
        vehicle.active_ride_id = None
        vehicle.mark_degraded = MagicMock()

        vehicles = {"V303": vehicle}

        degraded_repo = MagicMock()
        degraded_repo.add_vehicle = MagicMock()

        FleetManager(stations=stations, vehicles=vehicles, degraded_repo=degraded_repo)

        degraded_repo.add_vehicle.assert_called_once_with("V303")
        vehicle.mark_degraded.assert_called_once()

    def test_uses_injected_dependencies(self):
        stations = {1: MagicMock()}
        vehicles = {}

        active = ActiveRidesRegistry()
        repo = DegradedRepo(container_id=-1, _vehicle_ids=set(), name="Degraded Repo")
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
        vehicles = {}

        fm1 = FleetManager(stations=stations, vehicles=vehicles)
        fm2 = FleetManager(stations=stations, vehicles=vehicles)

        # Proves you avoided the "mutable default args" trap
        assert fm1.active_rides is not fm2.active_rides
        assert fm1.degraded_repo is not fm2.degraded_repo
        assert fm1.billing_service is not fm2.billing_service

    def test_initialize_state_raises_if_vehicle_has_active_ride_at_bootstrap(self):
        vehicle = MagicMock()
        vehicle.active_ride_id = 999
        vehicle.is_eligible.return_value = False
        vehicle.station_id = 1
        vehicle.mark_degraded = MagicMock()

        station = MagicMock()
        stations = {1: station}
        vehicles = {"V105": vehicle}

        with pytest.raises(InvalidInputError):
            FleetManager(stations=stations, vehicles=vehicles)

    # -----------------------------
    # User Registration Tests
    # -----------------------------
    def test_register_user_creates_and_stores_user_and_returns_id(self):
        fm = FleetManager(stations={}, vehicles={})

        user_id = fm.register_user("tok_test")

        assert isinstance(user_id, int)
        assert user_id in fm.users
        assert fm.users[user_id].user_id == user_id
        assert fm.users[user_id].payment_token == "tok_test"

    def test_register_user_rejects_blank_token(self):
        fm = FleetManager(stations={}, vehicles={})

        with pytest.raises(InvalidInputError):
            fm.register_user("")

        with pytest.raises(InvalidInputError):
            fm.register_user("   ")

    def test_register_user_rejects_non_string_token(self):
        fm = FleetManager(stations={}, vehicles={})

        with pytest.raises(InvalidInputError):
            fm.register_user(None)

    def test_register_user_rejects_exact_duplicate_token(self):
        fm = FleetManager(stations={}, vehicles={})

        fm.register_user("tok_test")

        with pytest.raises(ConflictError):
            fm.register_user("tok_test")

    def test_register_user_rejects_whitespace_variant_duplicate(self):
        fm = FleetManager(stations={}, vehicles={})

        fm.register_user("tok")

        with pytest.raises(ConflictError):
            fm.register_user(" tok ")

    def test_register_user_stores_normalized_token(self):
        fm = FleetManager(stations={}, vehicles={})

        user_id = fm.register_user(" tok_test ")

        assert fm.users[user_id].payment_token == "tok_test"

    #-----------------------------
    # Nearest Station Tests
    #-----------------------------
    def test_find_nearest_station_with_available_vehicle(self):
        stations = {
            1: MagicMock(lat=0.0, lon=0.0, has_available_vehicle=MagicMock(return_value=True), container_id=1),
            2: MagicMock(lat=10.0, lon=10.0, has_available_vehicle=MagicMock(return_value=True), container_id=2),
            3: MagicMock(lat=20.0, lon=20.0, has_available_vehicle=MagicMock(return_value=False), container_id=3),
        }
        fm = FleetManager(stations=stations, vehicles={})

        nearest = fm.nearest_station_with_available_vehicle((1.0, 1.0))
        assert nearest is stations[1]  # Station 1 is closer than Station 2

        nearest = fm.nearest_station_with_available_vehicle((15.0, 15.0))
        assert nearest is stations[2]  # Station 2 is closer than Station 1

        nearest = fm.nearest_station_with_available_vehicle((100.0, 100.0))
        assert nearest is stations[2]  # Station 2 is the only one with available vehicles

    def test_nearest_station_returns_none_when_no_available(self):
        stations = {
            1: MagicMock(lat=0.0, lon=0.0, has_available_vehicle=MagicMock(return_value=False), container_id=1),
            2: MagicMock(lat=1.0, lon=1.0, has_available_vehicle=MagicMock(return_value=False), container_id=2),
        }
        fm = FleetManager(stations=stations, vehicles={})

        assert fm.nearest_station_with_available_vehicle((0.0, 0.0)) is None

    #-----------------------------
    # Ride start Tests
    #-----------------------------
    def test_start_ride_user_does_not_exist_raises(self):
        fm = FleetManager(stations={}, vehicles={}, active_rides=ActiveRidesRegistry())
        fm.users = {}

        with pytest.raises(NotFoundError, match="User does not exist"):
            fm.start_ride(user_id=1, location=(0.0, 0.0))

    def test_start_ride_user_already_has_active_ride_raises(self):
        fm = FleetManager(stations={}, vehicles={}, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}

        # simulate active ride for user
        fm.active_rides.rides_by_user[1] = 999

        with pytest.raises(ConflictError, match="already has an active ride"):
            fm.start_ride(user_id=1, location=(0.0, 0.0))

    def test_start_ride_no_station_available_returns_none_payload(self):
        fm = FleetManager(stations={}, vehicles={}, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}

        fm.nearest_station_with_available_vehicle = MagicMock(return_value=None)

        result = fm.start_ride(user_id=1, location=(0.0, 0.0))
        assert result is None

    def test_start_ride_happy_path_registers_ride_and_mutates_station_vehicle(self, monkeypatch):
        fm = FleetManager(stations={}, vehicles={}, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}

        # Station with vehicles {10, 11}
        station = MagicMock()
        station.lat = 10.0
        station.lon = 20.0
        station.container_id = 7
        station.get_vehicle_ids.return_value = {10, 11}
        station.remove_vehicle = MagicMock()

        fm.nearest_station_with_available_vehicle = MagicMock(return_value=station)

        # Vehicles - selection is based on (rides_since_last_treated, vid) in your code
        v10 = MagicMock(rides_since_last_treated=5)
        v10.checkout_to_ride = MagicMock()
        v11 = MagicMock(rides_since_last_treated=1)
        v11.checkout_to_ride = MagicMock()
        fm.vehicles = {10: v10, 11: v11}

        fm._generate_ride_id = MagicMock(return_value=123)

        # IMPORTANT: your implementation must generate ride_id before checkout_to_ride
        # If it's still after, this test will crash with UnboundLocalError.
        ride = fm.start_ride(user_id=1, location=(0.0, 0.0))

        station.remove_vehicle.assert_called_once_with(11)
        v11.checkout_to_ride.assert_called_once_with(ride_id=123)
        v10.checkout_to_ride.assert_not_called()

        assert ride.ride_id == 123
        assert ride.user_id == 1
        assert ride.vehicle_id == 11
        assert ride.start_station_id == 7
        assert isinstance(ride.start_time, datetime.datetime)

        # Confirm registry contains it
        assert fm.active_rides.get(123) is ride
        assert fm.active_rides.has_active_ride_for_user(1) is True


    def test_start_ride_when_registry_rejects_ride_raises_value_error(self):
        fm = FleetManager(stations={}, vehicles={}, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}

        station = MagicMock()
        station.lat = 0.0
        station.lon = 0.0
        station.container_id = 1
        station.get_vehicle_ids.return_value = {10}
        station.remove_vehicle = MagicMock()
        fm.nearest_station_with_available_vehicle = MagicMock(return_value=station)

        v10 = MagicMock(rides_since_last_treated=0)
        v10.checkout_to_ride = MagicMock()
        fm.vehicles = {10: v10}

        fm._generate_ride_id = MagicMock(return_value=999)

        # Pre-fill registry with ride_id=999 to force add() ValueError
        fm.active_rides.rides[999] = MagicMock()
        fm.active_rides.rides_by_user[123] = 999  # doesn't matter which user

        with pytest.raises(ConflictError, match="Cannot start ride:"):
            fm.start_ride(user_id=1, location=(0.0, 0.0))

    def test_start_ride_deterministic_vehicle_selection_tie_breaks_by_smallest_id(self):
        station = MagicMock()
        station.container_id = 1
        station.lat = 0.0
        station.lon = 0.0
        station.has_available_vehicle.return_value = True
        station.get_vehicle_ids.return_value = {10, 11, 12}
        station.remove_vehicle = MagicMock()
        station.add_vehicle = MagicMock()  # needed for _initialize_state

        # Vehicles (make them bootstrap-valid)
        v10 = MagicMock(rides_since_last_treated=1)
        v10.checkout_to_ride = MagicMock()
        v10.is_eligible.return_value = True
        v10.station_id = 1
        v10.active_ride_id = None

        v11 = MagicMock(rides_since_last_treated=1)
        v11.checkout_to_ride = MagicMock()
        v11.is_eligible.return_value = True
        v11.station_id = 1
        v11.active_ride_id = None

        v12 = MagicMock(rides_since_last_treated=5)
        v12.checkout_to_ride = MagicMock()
        v12.is_eligible.return_value = True
        v12.station_id = 1
        v12.active_ride_id = None

        vehicles = {10: v10, 11: v11, 12: v12}
        stations = {1: station}

        fm = FleetManager(stations=stations, vehicles=vehicles, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}
        fm.nearest_station_with_available_vehicle = MagicMock(return_value=station)
        fm._generate_ride_id = MagicMock(return_value=99)

        ride = fm.start_ride(user_id=1, location=(0.0, 0.0))

        assert ride is not None
        assert ride.vehicle_id == 10  # tie-break by smallest id

        station.remove_vehicle.assert_called_once_with(10)
        v10.checkout_to_ride.assert_called_once_with(ride_id=99)
        v11.checkout_to_ride.assert_not_called()
        v12.checkout_to_ride.assert_not_called()

    def test_start_ride_updates_station_inventory_removes_selected_vehicle_only(self):
        inventory = {10, 11, 12}

        station = MagicMock()
        station.container_id = 1
        station.lat = 0.0
        station.lon = 0.0
        station.has_available_vehicle.return_value = True
        station.get_vehicle_ids.side_effect = lambda: set(inventory)
        station.add_vehicle = MagicMock()  # needed for _initialize_state

        def remove_vehicle(vid):
            inventory.remove(vid)

        station.remove_vehicle.side_effect = remove_vehicle

        v10 = MagicMock(rides_since_last_treated=3)
        v10.checkout_to_ride = MagicMock()
        v10.is_eligible.return_value = True
        v10.station_id = 1
        v10.active_ride_id = None

        v11 = MagicMock(rides_since_last_treated=0)
        v11.checkout_to_ride = MagicMock()
        v11.is_eligible.return_value = True
        v11.station_id = 1
        v11.active_ride_id = None

        v12 = MagicMock(rides_since_last_treated=2)
        v12.checkout_to_ride = MagicMock()
        v12.is_eligible.return_value = True
        v12.station_id = 1
        v12.active_ride_id = None

        vehicles = {10: v10, 11: v11, 12: v12}
        stations = {1: station}

        fm = FleetManager(stations=stations, vehicles=vehicles, active_rides=ActiveRidesRegistry())
        fm.users = {1: MagicMock()}
        fm.nearest_station_with_available_vehicle = MagicMock(return_value=station)
        fm._generate_ride_id = MagicMock(return_value=100)

        ride = fm.start_ride(user_id=1, location=(0.0, 0.0))

        assert ride is not None
        assert ride.vehicle_id == 11
        assert inventory == {10, 12}
