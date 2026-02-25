from fastapi import APIRouter
from src.api.routes.health import router as health_router
from src.api.routes.users import router as users_router
from src.api.routes.rides import router as rides_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(rides_router, prefix="/rides", tags=["rides"])