from fastapi import FastAPI

from src.api.exceptions_handler import register_exception_handlers
from src.api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vehicle Sharing API",
        description="API for managing vehicle sharing services",
        version="1.0.0",
    )

    app.include_router(api_router)
    register_exception_handlers(app)
    return app


app = create_app()
