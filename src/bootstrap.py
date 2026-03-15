from pathlib import Path

from src.data.loaders import StationDataLoader, VehicleDataLoader
from src.data.state_serializer import load_state
from src.services.fleet_manager import FleetManager


def build_fleet_manager(
    stations_csv: Path,
    vehicles_csv: Path,
    state_path: Path = Path("data/state.json"),
) -> FleetManager:
    """
    Build and return a FleetManager from CSV base data and optional persisted state:
    - Load stations and vehicles from CSV
    - Initialize a normal FleetManager from the CSV-loaded base data
    - Apply persisted runtime state from state_path when the snapshot exists

    Notes:
    - FleetManager initialization is responsible for linking vehicles to stations
      and removing vehicles that require maintenance.
    """
    try:
        stations = StationDataLoader(stations_csv).create_objects()
        vehicles = VehicleDataLoader(vehicles_csv).create_objects()
    except (FileNotFoundError, ValueError) as e:
        raise RuntimeError(f"Bootstrap failed: {e}") from e

    fleet_manager = FleetManager(stations=stations, vehicles=vehicles)
    load_state(fleet_manager, state_path)
    return fleet_manager
