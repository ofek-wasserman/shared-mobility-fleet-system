"""
Data loading layer — Role 5 (Data + Persistence).

DataLoader       : abstract base; handles CSV I/O.
StationDataLoader: parses stations.csv → dict[int, Station].
VehicleDataLoader: parses vehicles.csv → dict[str, Vehicle].

NOTE: Station / Vehicle imports are commented out until the domain
layer (Role 4) stabilises. The loaders currently return validated
plain-dict rows so the rest of the pipeline can be tested
independently.  Swap in the real constructors once Role 4 merges.
"""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class DataLoader(ABC):
    """Read a CSV file and build a dictionary of domain objects."""

    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_objects(self) -> dict[Any, Any]:
        """Return a dict keyed by the domain object's primary key."""
        rows = self._load_rows()
        result: dict[Any, Any] = {}
        for row in rows:
            key, obj = self._parse_row(row)
            result[key] = obj
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_rows(self) -> list[dict[str, str]]:
        """Read every row of the CSV and return as a list of dicts."""
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.csv_path}"
            )
        with self.csv_path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            return [dict(row) for row in reader]

    @abstractmethod
    def _parse_row(self, row: dict[str, str]) -> tuple[Any, Any]:
        """Parse a single CSV row and return (primary_key, domain_object)."""


# ---------------------------------------------------------------------------
# Concrete loaders
# ---------------------------------------------------------------------------

class StationDataLoader(DataLoader):
    """
    Parses stations.csv.

    Expected columns:
        station_id, name, lat, lon, max_capacity
    """

    def _parse_row(self, row: dict[str, str]) -> tuple[int, dict]:
        station_id = int(row["station_id"])
        parsed = {
            "station_id": station_id,
            "name": row["name"].strip(),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "max_capacity": int(row["max_capacity"]),
        }

        # TODO: replace the dict below with the real constructor once
        #       the domain layer is merged:
        #
        #   from src.domain.models import Station
        #   obj = Station(
        #       station_id=parsed["station_id"],
        #       name=parsed["name"],
        #       lat=parsed["lat"],
        #       lon=parsed["lon"],
        #       max_capacity=parsed["max_capacity"],
        #   )
        #   return station_id, obj

        return station_id, parsed


class VehicleDataLoader(DataLoader):
    """
    Parses vehicles.csv.

    Expected columns:
        vehicle_id, type, status, rides_since_last_treated,
        last_treated_date, station_id, charge_pct

    charge_pct is empty for non-electric vehicles (Bicycle).
    """

    def _parse_row(self, row: dict[str, str]) -> tuple[str, dict]:
        vehicle_id = row["vehicle_id"].strip()
        charge_raw = row.get("charge_pct", "").strip()

        parsed = {
            "vehicle_id": vehicle_id,
            "type": row["type"].strip(),
            "status": row["status"].strip(),
            "rides_since_last_treated": int(row["rides_since_last_treated"]),
            "last_treated_date": date.fromisoformat(row["last_treated_date"]),
            "station_id": int(row["station_id"]),
            # None for non-electric (Bicycle)
            "charge_pct": int(charge_raw) if charge_raw else None,
        }

        # TODO: replace the dict below with the real constructor once
        #       the domain layer is merged:
        #
        #   from src.domain.models import Bicycle, EBike, Scooter, VehicleType
        #   vehicle_type = VehicleType[parsed["type"]]
        #   cls_map = {
        #       VehicleType.BICYCLE: Bicycle,
        #       VehicleType.E_BIKE: EBike,
        #       VehicleType.SCOOTER: Scooter,
        #   }
        #   obj = cls_map[vehicle_type](...)
        #   return vehicle_id, obj

        return vehicle_id, parsed
