"""Unit tests for KAN-31 — VehicleDataLoader."""
import csv
from datetime import date
from pathlib import Path

import pytest

from src.data.loaders import VehicleDataLoader

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

    def test_vehicle_type_is_string(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle["vehicle_type"] == "bicycle"

    def test_electric_bicycle_type(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000002"]
        assert vehicle["vehicle_type"] == "electric_bicycle"

    def test_last_treated_date_is_date_object(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle["last_treated_date"], date)
        assert vehicle["last_treated_date"] == date(2025, 1, 16)

    def test_rides_since_last_treated_is_int(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle["rides_since_last_treated"], int)
        assert vehicle["rides_since_last_treated"] == 3

    def test_station_id_is_int(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        _write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle["station_id"] == 1001

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            VehicleDataLoader(tmp_path / "missing.csv").create_objects()
