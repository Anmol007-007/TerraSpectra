"""Application configuration using pydantic-settings."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    # Graceful fallback when pydantic-settings is not installed in the active environment
    class BaseSettings(BaseModel):  # type: ignore[no-redef]
        """Fallback BaseSettings using standard Pydantic BaseModel."""

    class SettingsConfigDict(dict):  # type: ignore[no-redef]
        """Fallback SettingsConfigDict."""
        def __init__(self, **kwargs: Any) -> None:
            super().__init__(**kwargs)

DeviceType = Literal["auto", "cpu", "cuda"]


class Settings(BaseSettings):
    """Global configuration settings for TerraSpectra."""

    model_config = SettingsConfigDict(
        env_prefix="TS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = Field(default="development", description="Runtime environment name")
    data_dir: Path = Field(default=Path("data"), description="Path to base data directory")
    models_dir: Path = Field(
        default=Path("models_store"), description="Path to model checkpoints store"
    )
    device: DeviceType = Field(
        default="auto", description="Compute device selection ('auto', 'cpu', or 'cuda')"
    )
    max_upload_mb: int = Field(
        default=500, description="Maximum scene upload file size in megabytes"
    )
    api_key: str | None = Field(default=None, description="Optional API key for client auth")

    @property
    def raw_data_dir(self) -> Path:
        """Directory containing raw hyperspectral cubes."""
        return self.data_dir / "raw"

    @property
    def interim_data_dir(self) -> Path:
        """Directory for intermediate/preprocessed cubes."""
        return self.data_dir / "interim"

    @property
    def processed_data_dir(self) -> Path:
        """Directory for analysis-ready tensor cubes."""
        return self.data_dir / "processed"

    @property
    def synthetic_data_dir(self) -> Path:
        """Directory for generated synthetic cubes."""
        return self.data_dir / "synthetic"

    @property
    def catalog_path(self) -> Path:
        """Path to scene catalog JSON file."""
        return self.data_dir / "catalog" / "scenes.json"


settings = Settings()
