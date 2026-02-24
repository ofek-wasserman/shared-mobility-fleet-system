import csv
from datetime import date
from pathlib import Path

import pytest

from src.data.loaders import StationDataLoader, VehicleDataLoader

# ── helpers ──────────────────────────────────────────────────────────────────

def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


STATION_ROWS = [
    {"station_id": "1", "name": "Dizengoff Sq", "lat": "32.0796", "lon": "34.7739", "max_capacity": "10"},
    {"station_id": "2", "name": "Central Bus Station", "lat": "32.0577", "lon": "34.7799", "max_capacity": "15"},
]

VEHICLE_ROWS = [
    {
        "vehicle_id": "V000001", "vehicle_type": "bicycle", "status": "available",
        "rides_since_last_treated": "3", "last_treated_date": "2025-01-16",
        "station_id": "1",
    },
    {
        "vehicle_id": "V000002", "vehicle_type": "electric_bicycle", "status": "available",
        "rides_since_last_treated": "0", "last_treated_date": "2025-03-28",
        "station_id": "1",
    },
]


# ── StationDataLoader ─────────────────────────────────────────────────────────

class TestStationDataLoader:

    def test_loads_correct_number_of_stations(self, tmp_path):
        csv_file = tmp_path / "stations.csv"
        write_csv(csv_file, STATION_ROWS)
        result = StationDataLoader(csv_file).create_objects()
        assert len(result) == 2

    def test_keys_are_ints(self, tmp_path):
        csv_file = tmp_path / "stations.csv"
        write_csv(csv_file, STATION_ROWS)
        result = StationDataLoader(csv_file).create_objects()
        assert all(isinstance(k, int) for k in result)

    def test_lat_lon_are_floats(self, tmp_path):
        csv_file = tmp_path / "stations.csv"
        write_csv(csv_file, STATION_ROWS)
        station = StationDataLoader(csv_file).create_objects()[1]
        assert isinstance(station["lat"], float)
        assert isinstance(station["lon"], float)

    def test_max_capacity_is_int(self, tmp_path):
        csv_file = tmp_path / "stations.csv"
        write_csv(csv_file, STATION_ROWS)
        station = StationDataLoader(csv_file).create_objects()[1]
        assert isinstance(station["max_capacity"], int)
        assert station["max_capacity"] == 10

    def test_name_is_stripped(self, tmp_path):
        rows = [{"station_id": "1", "name": "  Central  ", "lat": "32.0", "lon": "34.0", "max_capacity": "5"}]
        csv_file = tmp_path / "stations.csv"
        write_csv(csv_file, rows)
        station = StationDataLoader(csv_file).create_objects()[1]
        assert station["name"] == "Central"

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            StationDataLoader(tmp_path / "nonexistent.csv").create_objects()


# ── VehicleDataLoader ─────────────────────────────────────────────────────────

class TestVehicleDataLoader:

    def test_loads_correct_number_of_vehicles(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        write_csv(csv_file, VEHICLE_ROWS)
        result = VehicleDataLoader(csv_file).create_objects()
        assert len(result) == 2

    def test_keys_are_strings(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        write_csv(csv_file, VEHICLE_ROWS)
        result = VehicleDataLoader(csv_file).create_objects()
        assert all(isinstance(k, str) for k in result)

    def test_vehicle_type_is_string(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert vehicle["vehicle_type"] == "bicycle"

    def test_last_treated_date_is_date_object(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle["last_treated_date"], date)
        assert vehicle["last_treated_date"] == date(2025, 1, 16)

    def test_rides_since_last_treated_is_int(self, tmp_path):
        csv_file = tmp_path / "vehicles.csv"
        write_csv(csv_file, VEHICLE_ROWS)
        vehicle = VehicleDataLoader(csv_file).create_objects()["V000001"]
        assert isinstance(vehicle["rides_since_last_treated"], int)

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            VehicleDataLoader(tmp_path / "nonexistent.csv").create_objects()
