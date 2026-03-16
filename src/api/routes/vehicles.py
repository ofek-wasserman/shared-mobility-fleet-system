from fastapi import APIRouter, Depends, Request, status

from src.api.dependencies import get_fleet_manager
from src.api.schemas.vehicles import (
    ReportDegradedRequest,
    ReportDegradedResponse,
    TreatVehicleRequest,
    TreatVehicleResponse,
)
from src.data.state_serializer import save_state
from src.services.fleet_manager import FleetManager

router = APIRouter()


@router.post(
    "/vehicle/report-degraded",
    response_model=ReportDegradedResponse,
    status_code=status.HTTP_200_OK,
)
async def report_degraded(
    req: ReportDegradedRequest,
    request: Request,
    fleet_manager: FleetManager = Depends(get_fleet_manager),
) -> ReportDegradedResponse:
    fleet_manager.report_degraded(
        user_id=req.user_id,
        vehicle_id=req.vehicle_id,
    )
    save_state(fleet_manager, request.app.state.state_path)
    return ReportDegradedResponse(result="ok")


@router.post(
    "/vehicle/treat",
    response_model=TreatVehicleResponse,
    status_code=status.HTTP_200_OK,
)
async def treat_vehicle(
    req: TreatVehicleRequest,
    request: Request,
    fleet_manager: FleetManager = Depends(get_fleet_manager),
) -> TreatVehicleResponse:
    treated_vehicle_ids = fleet_manager.apply_treatment((req.lat, req.lon))
    save_state(fleet_manager, request.app.state.state_path)
    return TreatVehicleResponse(treated_vehicle_ids=treated_vehicle_ids)
