from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any

from src.domain.enums import VehicleStatus
from src.domain.Vehicle import Bicycle, EBike, Scooter, Vehicle


class DataLoader(ABC):
    """Abstract base class for CSV data loaders.

    Subclasses must implement ``_parse_row`` to convert each raw CSV
    row (dict of strings) into a ``(primary_key, domain_object)`` pair.
    ``create_objects`` drives the full load and returns a keyed dict.
    """

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    def create_objects(self) -> dict[Any, Any]:
        """Load the CSV and return a dict of parsed domain objects."""
        rows = self._load_rows()
        return dict(self._parse_row(row) for row in rows)

    def _load_rows(self) -> list[dict[str, str]]:
        """Read all rows from the CSV file. Raises FileNotFoundError if missing."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")
        with self.csv_path.open(newline="", encoding="utf-8") as fh:
            return list(csv.DictReader(fh))

    @abstractmethod
    def _parse_row(self, row: dict[str, str]) -> tuple[Any, Any]:
        """Return (primary_key, domain_object) for a single CSV row."""


class StationDataLoader(DataLoader):
    """Loads stations.csv → dict[int, dict].

    CSV columns: station_id, name, lat, lon, max_capacity.
    Keys are ``int`` station IDs.
    TODO: return Station domain objects once Role 4 domain layer is ready.
    """

    def _parse_row(self, row: dict[str, str]) -> tuple[int, dict]:
        """Parse one CSV row into (station_id: int, station_data: dict)."""
        station_id = int(row["station_id"])
        data = {
            "station_id": station_id,
            "name": row["name"].strip(),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "max_capacity": int(row["max_capacity"]),
        }
        return station_id, data


class VehicleDataLoader(DataLoader):
    """Loads vehicles.csv → dict[str, Vehicle].

    CSV columns: vehicle_id, station_id, vehicle_type, status,
                 rides_since_last_treated, last_treated_date.
    Keys are ``str`` vehicle IDs, values are Vehicle domain objects.
    """

    def _parse_row(self, row: dict[str, str]) -> tuple[str, Vehicle]:
        """Parse one CSV row into (vehicle_id: str, vehicle: Vehicle)."""
        vehicle_id = row["vehicle_id"].strip()
        vehicle_type = row["vehicle_type"].strip()
        status = VehicleStatus(row["status"].strip())
        rides_since_last_treated = int(row["rides_since_last_treated"])
        last_treated_date = date.fromisoformat(row["last_treated_date"])
        station_id = int(row["station_id"])

        # Electric vehicles start with 100% charge (no charge_pct in CSV)
        if vehicle_type == "bicycle":
            vehicle = Bicycle(
                vehicle_id=vehicle_id,
                status=status,
                rides_since_last_treated=rides_since_last_treated,
                last_treated_date=last_treated_date,
                station_id=station_id,
                active_ride_id=None,
            )
        elif vehicle_type == "electric_bicycle":
            vehicle = EBike(
                vehicle_id=vehicle_id,
                status=status,
                rides_since_last_treated=rides_since_last_treated,
                last_treated_date=last_treated_date,
                station_id=station_id,
                active_ride_id=None,
                charge_pct=100,
            )
        elif vehicle_type == "scooter":
            vehicle = Scooter(
                vehicle_id=vehicle_id,
                status=status,
                rides_since_last_treated=rides_since_last_treated,
                last_treated_date=last_treated_date,
                station_id=station_id,
                active_ride_id=None,
                charge_pct=100,
            )
        else:
            raise ValueError(f"Unknown vehicle type: {vehicle_type}")

        return vehicle_id, vehicle
