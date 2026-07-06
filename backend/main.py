"""NutriGenie AI — FastAPI application entry point."""

import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from backend.api.config import settings
from backend.routes import (
    auth,
    chat,
    meal_plan,
    image_analysis,
    food_swap,
    label_analysis,
    dashboard,
    profile,
)

logger = structlog.get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    """Manage application startup and shutdown events."""
    logger.info("NutriGenie AI starting up", version=settings.APP_VERSION)
    yield
    logger.info("NutriGenie AI shutting down")


def create_application() -> FastAPI:
    """Factory function that creates and configures the FastAPI application."""
    application = FastAPI(
        title="NutriGenie AI",
        description="Intelligent Nutrition Assistant powered by IBM Granite & watsonx.ai",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # Rate limiter
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Middleware
    application.add_middleware(GZipMiddleware, minimum_size=1000)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    application.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    application.include_router(chat.router, prefix="/chat", tags=["AI Chat"])
    application.include_router(meal_plan.router, prefix="/meal-plan", tags=["Meal Planner"])
    application.include_router(image_analysis.router, prefix="/image-analysis", tags=["Image Analysis"])
    application.include_router(food_swap.router, prefix="/food-swap", tags=["Food Swap"])
    application.include_router(label_analysis.router, prefix="/label-analysis", tags=["Label Analysis"])
    application.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
    application.include_router(profile.router, prefix="/profile", tags=["Profile"])

    return application


app = create_application()
