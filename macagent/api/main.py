"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from macagent.api.routers import sessions, actions, analyze, users
from macagent.core.logger import logger
from macagent.core.config import settings


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="MacAgent API",
        description="VLM-based Mac application automation system",
        version="0.1.0",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(sessions.router, prefix="/api/v1")
    app.include_router(actions.router, prefix="/api/v1")
    app.include_router(analyze.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "MacAgent API",
            "version": "0.1.0",
            "status": "running",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.on_event("startup")
    async def startup_event():
        """Run on application startup."""
        logger.info("MacAgent API starting up...")
        logger.info(f"Using VLM model: {settings.vlm_model}")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Run on application shutdown."""
        logger.info("MacAgent API shutting down...")

    return app


# Create app instance
app = create_app()
