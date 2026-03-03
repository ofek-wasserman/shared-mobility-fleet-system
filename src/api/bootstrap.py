from __future__ import annotations

from pathlib import Path

from src.data.loaders import StationDataLoader, VehicleDataLoader
from src.services.fleet_manager import FleetManager


def build_fleet_manager(
    stations_path: Path | str = Path("data/stations.csv"),
    vehicles_path: Path | str = Path("data/vehicles.csv"),
) -> FleetManager:
    """
    API bootstrap helper.

    Loads stations/vehicles from CSV via the data layer, links vehicles into
    station inventories, then constructs a FleetManager.

    The linking step is required because FleetManager._initialize_state()
    may remove vehicles from stations, and Station.remove_vehicle() raises
    KeyError if the vehicle_id is not present.
    """
    stations = StationDataLoader(stations_path).create_objects()
    vehicles = VehicleDataLoader(vehicles_path).create_objects()

    # Link vehicles into their stations so FleetManager initialization is consistent
    for vehicle_id, vehicle in vehicles.items():
        station = stations.get(vehicle.station_id)
        if station is not None:
            station.add_vehicle(vehicle_id)

    return FleetManager(stations=stations, vehicles=vehicles)
