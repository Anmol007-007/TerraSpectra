"""Scene catalog management and automated dataset directory scanner."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from terraspectra.core.paths import ensure_dir
from terraspectra.core.schemas import SceneMetadata
from terraspectra.core.settings import settings
from terraspectra.data.readers import get_reader


class SceneCatalog:
    """Catalog of indexed hyperspectral satellite scenes."""

    def __init__(self, scenes: list[SceneMetadata] | None = None) -> None:
        self.scenes: list[SceneMetadata] = scenes or []

    def add(self, metadata: SceneMetadata) -> None:
        """Add or update scene record in catalog."""
        self.scenes = [s for s in self.scenes if s.scene_id != metadata.scene_id]
        self.scenes.append(metadata)

    def get(self, scene_id: str) -> SceneMetadata | None:
        """Find scene record by ID."""
        for s in self.scenes:
            if s.scene_id == scene_id:
                return s
        return None

    def list_scenes(self) -> list[SceneMetadata]:
        """Return all cataloged scenes."""
        return list(self.scenes)

    def save(self, path: str | Path | None = None) -> Path:
        """Save scene catalog to JSON file."""
        p = Path(path) if path else settings.catalog_path
        ensure_dir(p.parent)
        data = [s.model_dump() for s in self.scenes]
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return p

    @classmethod
    def load(cls, path: str | Path | None = None) -> SceneCatalog:
        """Load catalog from JSON file."""
        p = Path(path) if path else settings.catalog_path
        if not p.exists():
            return cls([])
        data = json.loads(p.read_text(encoding="utf-8"))
        scenes = [SceneMetadata(**item) for item in data]
        return cls(scenes)


def scan_directory_for_scenes(directory: str | Path) -> SceneCatalog:
    """Scan directory recursively for GeoTIFF and HDF5 rasters and build a catalog."""
    dir_path = Path(directory)
    catalog = SceneCatalog()

    valid_exts = {".tif", ".tiff", ".h5", ".hdf5", ".npz"}
    for f in dir_path.rglob("*"):
        if f.is_file() and f.suffix.lower() in valid_exts and not f.name.endswith("_meta.json"):
            try:
                reader = get_reader(f)
                meta = reader.get_metadata()
                catalog.add(meta)
            except Exception:
                continue

    return catalog
