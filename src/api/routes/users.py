from fastapi import APIRouter, Depends, Request, status

from src.api.dependencies import get_fleet_manager
from src.api.schemas.users import RegisterRequest, RegisterResponse
from src.data.state_serializer import save_state
from src.services.fleet_manager import FleetManager

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    req: RegisterRequest,
    request: Request,
    fleet_manager: FleetManager = Depends(get_fleet_manager),
) -> RegisterResponse:
    user_id = fleet_manager.register_user(req.payment_token)
    save_state(fleet_manager, request.app.state.state_path)
    return RegisterResponse(user_id=user_id)
