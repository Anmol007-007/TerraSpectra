"""TerraSpectra FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from terraspectra import __version__


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI instance.
    """
    app = FastAPI(
        title="TerraSpectra",
        description="Hyperspectral crop disease forecasting API",
        version=__version__,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Liveness probe endpoint."""
        return {"status": "ok", "version": __version__}

    return app


app: FastAPI = create_app()
