"""Application configuration using pydantic-settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
