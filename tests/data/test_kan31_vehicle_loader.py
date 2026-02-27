"""Unit tests for KAN-31 — VehicleDataLoader."""

import csv
from datetime import date
from pathlib import Path

import pytest

from src.data.loaders import VehicleDataLoader
from src.domain.enums import VehicleLocation, VehicleStatus
from src.domain.Vehicle import Bicycle, EBike, Vehicle

VEHICLE_ROWS = [
    {
        "vehicle_id": "V000001",
        "station_id": "1001",
        "vehicle_type": "bicycle",
        "status": "available",
        "rides_since_last_treated": "3",
        "last_treated_date": "2025-01-16",
    },
    {
        "vehicle_id": "V000002",
        "station_id": "1001",
        "vehicle_type": "electric_bicycle",
        "status": "available",
        "rides_since_last_treated": "0",
        "last_treated_date": "2025-03-28",
    },
]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


class TestVehicleDataLoader:
    def test_loads_correct_count(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        result = VehicleDataLoader(csv_file).create_objects()
        assert len(result) == 2

    def test_keys_are_strings(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        result = VehicleDataLoader(csv_file).create_objects()
        assert all(isinstance(k, str) for k in result)

    def test_values_are_vehicle_objects(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        result = VehicleDataLoader(csv_file).create_objects()
        assert all(isinstance(v, Vehicle) for v in result.values())

    def test_bicycle_creates_bicycle_instance(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle, Bicycle)

    def test_electric_bicycle_creates_ebike_instance(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000002"]
        assert isinstance(vehicle, EBike)

    def test_last_treated_date_is_date_object(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle.last_treated_date, date)
        assert vehicle.last_treated_date == date(2025, 1, 16)

    def test_rides_since_last_treated_is_int(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle.rides_since_last_treated, int)
        assert vehicle.rides_since_last_treated == 3

    def test_station_id_is_int(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle.station_id, int)
        assert vehicle.station_id == 1001

    def test_status_is_enum(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle.status == VehicleStatus.AVAILABLE

    def test_location_is_docked_when_station_id_present(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle.location == VehicleLocation.DOCKED

    def test_active_ride_id_is_none(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle.active_ride_id is None

    def test_electric_vehicle_charge_initialized(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000002"]
        assert vehicle.charge_pct == 100

    def test_vehicle_id_matches(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicles = VehicleDataLoader(csv_file).create_objects()
        assert vehicles["V000001"].vehicle_id == "V000001"
        assert vehicles["V000002"].vehicle_id == "V000002"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            VehicleDataLoader(tmp_path / "missing.csv").create_objects()
