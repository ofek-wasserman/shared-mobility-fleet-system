from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.bootstrap import build_fleet_manager
from src.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vehicle Sharing API",
        description="API for managing vehicle sharing services",
        version="1.0.0",
    )

    # Bootstrap: load initial state + build FleetManager once for app lifetime
    app.state.fleet_manager = build_fleet_manager(
        stations_path=Path("data/stations.csv"),
        vehicles_path=Path("data/vehicles.csv"),
    )

    # Routes
    app.include_router(api_router)

    # Map FastAPI validation errors (default 422) to 400
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.errors()})

    return app


app = create_app()
