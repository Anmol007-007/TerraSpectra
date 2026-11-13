"""Abstract and concrete hyperspectral cube readers with windowed I/O."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from numpy.typing import NDArray

from terraspectra.core.constants import DEFAULT_CRS, GSD_M, NODATA
from terraspectra.core.errors import DataError, SceneNotFoundError
from terraspectra.core.schemas import GeoBounds, SceneMetadata
from terraspectra.data.windows import Window, WindowLRUCache


class CubeReader(ABC):
    """Abstract reader interface for hyperspectral satellite rasters."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        if not self.path.exists():
            # Check for npz/json fallbacks
            if self.path.with_suffix(".npz").exists():
                self.path = self.path.with_suffix(".npz")
            else:
                raise SceneNotFoundError(f"Scene raster file not found: {self.path}")
        self._cache = WindowLRUCache(maxsize=16)

    @property
    @abstractmethod
    def shape(self) -> tuple[int, int, int]:
        """Return (bands, rows, cols) tuple."""

    @property
    def bands(self) -> int:
        return self.shape[0]

    @property
    def rows(self) -> int:
        return self.shape[1]

    @property
    def cols(self) -> int:
        return self.shape[2]

    @property
    @abstractmethod
    def wavelengths_nm(self) -> NDArray[np.float32]:
        """Return 1-D array of band center wavelengths."""

    @property
    @abstractmethod
    def crs(self) -> str:
        """Return coordinate reference system."""

    @property
    @abstractmethod
    def transform(self) -> tuple[float, float, float, float, float, float]:
        """Return 6-element GDAL/Affine transform tuple."""

    @abstractmethod
    def read_window(
        self,
        window: Window,
        bands: list[int] | None = None,
        out_shape: tuple[int, int] | None = None,
    ) -> NDArray[np.float32]:
        """Read a sub-window of the cube into RAM as float32 [B_sub, H_sub, W_sub]."""

    def read_full(self, bands: list[int] | None = None) -> NDArray[np.float32]:
        """Read full scene cube (use with caution on large scenes)."""
        win = Window(row_off=0, col_off=0, height=self.rows, width=self.cols)
        return self.read_window(win, bands=bands)

    def iter_band_chunks(self, chunk_bands: int = 32) -> Iterator[tuple[range, NDArray[np.float32]]]:
        """Lazily stream band chunks for memory-bounded processing."""
        for b_start in range(0, self.bands, chunk_bands):
            b_end = min(self.bands, b_start + chunk_bands)
            b_range = range(b_start, b_end)
            data = self.read_full(bands=list(b_range))
            yield (b_range, data)

    def get_metadata(self) -> SceneMetadata:
        """Extract standardized Pydantic SceneMetadata."""
        c = self.transform
        west = c[0]
        north = c[3]
        east = west + self.cols * c[1]
        south = north + self.rows * c[5]

        bounds = GeoBounds(west=west, south=south, east=east, north=north, crs=self.crs)
        size_mb = self.path.stat().st_size / (1024.0 * 1024.0)

        return SceneMetadata(
            scene_id=self.path.stem,
            path=str(self.path),
            format="GeoTIFF" if self.path.suffix in (".tif", ".tiff") else "HDF5",
            bands=self.bands,
            rows=self.rows,
            cols=self.cols,
            crs=self.crs,
            bounds=bounds,
            gsd_m=GSD_M,
            acquired_date="2026-06-01T10:00:00Z",
            size_mb=round(size_mb, 2),
        )


class GeoTiffReader(CubeReader):
    """Rasterio-based reader for GeoTIFF hyperspectral data cubes."""

    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._rasterio_ds = None
        self._npz_data = None

        if self.path.suffix in (".tif", ".tiff"):
            try:
                import rasterio
                self._rasterio_ds = rasterio.open(self.path)
            except (ImportError, Exception):
                # Fallback to companion npz if exists
                if self.path.with_suffix(".npz").exists():
                    self.path = self.path.with_suffix(".npz")
                    self._npz_data = np.load(self.path)
                else:
                    raise DataError(f"Cannot open TIFF without rasterio: {self.path}")
        else:
            self._npz_data = np.load(self.path)

    @property
    def shape(self) -> tuple[int, int, int]:
        if self._rasterio_ds:
            return (self._rasterio_ds.count, self._rasterio_ds.height, self._rasterio_ds.width)
        arr = self._npz_data["cube"]
        return arr.shape

    @property
    def wavelengths_nm(self) -> NDArray[np.float32]:
        if self._rasterio_ds:
            wls = []
            for b in range(1, self.bands + 1):
                desc = self._rasterio_ds.descriptions[b - 1] or ""
                # Parse wavelength if formatted as 'Wavelength XXX.XX nm'
                parts = desc.split()
                if len(parts) >= 2 and parts[1].replace(".", "", 1).isdigit():
                    wls.append(float(parts[1]))
                else:
                    wls.append(400.0 + (b - 1) * 9.4)
            return np.array(wls, dtype=np.float32)
        return self._npz_data["wavelengths_nm"]

    @property
    def crs(self) -> str:
        if self._rasterio_ds:
            return str(self._rasterio_ds.crs or DEFAULT_CRS)
        return str(self._npz_data.get("crs", DEFAULT_CRS))

    @property
    def transform(self) -> tuple[float, float, float, float, float, float]:
        if self._rasterio_ds:
            t = self._rasterio_ds.transform
            return (t.c, t.a, t.b, t.f, t.d, t.e)
        t_arr = self._npz_data.get("transform")
        if t_arr is not None and len(t_arr) == 6:
            return tuple(float(x) for x in t_arr)
        return (500000.0, float(GSD_M), 0.0, 3160000.0, 0.0, -float(GSD_M))

    def read_window(
        self,
        window: Window,
        bands: list[int] | None = None,
        out_shape: tuple[int, int] | None = None,
    ) -> NDArray[np.float32]:
        cached = self._cache.get(window)
        if cached is not None and bands is None and out_shape is None:
            return cached

        if self._rasterio_ds:
            import rasterio
            from rasterio.windows import Window as RWindow

            rwin = RWindow(
                col_off=window.col_off,
                row_off=window.row_off,
                width=window.width,
                height=window.height,
            )
            # Rasterio uses 1-based band indexes
            indexes = [b + 1 for b in bands] if bands else None
            arr = self._rasterio_ds.read(indexes=indexes, window=rwin, out_shape=out_shape).astype(np.float32)
        else:
            raw = self._npz_data["cube"]
            b_slice = slice(None) if bands is None else bands
            arr = raw[b_slice, window.row_off : window.row_off + window.height, window.col_off : window.col_off + window.width]
            if out_shape:
                from scipy.ndimage import zoom
                zh = out_shape[0] / arr.shape[1]
                zw = out_shape[1] / arr.shape[2]
                arr = zoom(arr, (1.0, zh, zw), order=1)

        self._cache.put(window, arr)
        return arr.astype(np.float32)


class Hdf5Reader(CubeReader):
    """HDF5 chunked cube reader using h5py with fallback."""

    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._h5_file = None
        self._npz_data = None

        if self.path.suffix in (".h5", ".hdf5"):
            try:
                import h5py
                self._h5_file = h5py.File(self.path, "r")
            except (ImportError, Exception):
                if self.path.with_suffix(".npz").exists():
                    self.path = self.path.with_suffix(".npz")
                    self._npz_data = np.load(self.path)
                else:
                    raise DataError(f"Cannot read HDF5: {self.path}")
        else:
            self._npz_data = np.load(self.path)

    @property
    def shape(self) -> tuple[int, int, int]:
        if self._h5_file:
            return self._h5_file["/cube"].shape
        return self._npz_data["cube"].shape

    @property
    def wavelengths_nm(self) -> NDArray[np.float32]:
        if self._h5_file:
            attrs = self._h5_file["/cube"].attrs
            if "wavelengths_nm" in attrs:
                return np.asarray(attrs["wavelengths_nm"], dtype=np.float32)
            return np.linspace(400.0, 2500.0, self.bands, dtype=np.float32)
        return self._npz_data["wavelengths_nm"]

    @property
    def crs(self) -> str:
        if self._h5_file:
            return str(self._h5_file["/cube"].attrs.get("crs", DEFAULT_CRS))
        return str(self._npz_data.get("crs", DEFAULT_CRS))

    @property
    def transform(self) -> tuple[float, float, float, float, float, float]:
        if self._h5_file:
            t = self._h5_file["/cube"].attrs.get("transform")
            if t is not None:
                return tuple(float(x) for x in t)
        return (500000.0, float(GSD_M), 0.0, 3160000.0, 0.0, -float(GSD_M))

    def read_window(
        self,
        window: Window,
        bands: list[int] | None = None,
        out_shape: tuple[int, int] | None = None,
    ) -> NDArray[np.float32]:
        cached = self._cache.get(window)
        if cached is not None and bands is None and out_shape is None:
            return cached

        dset = self._h5_file["/cube"] if self._h5_file else self._npz_data["cube"]
        b_slice = slice(None) if bands is None else bands
        arr = dset[b_slice, window.row_off : window.row_off + window.height, window.col_off : window.col_off + window.width]

        if out_shape:
            from scipy.ndimage import zoom
            zh = out_shape[0] / arr.shape[1]
            zw = out_shape[1] / arr.shape[2]
            arr = zoom(arr, (1.0, zh, zw), order=1)

        self._cache.put(window, arr)
        return arr.astype(np.float32)


def get_reader(path: str | Path) -> CubeReader:
    """Factory creating appropriate CubeReader based on file format extension."""
    p = Path(path)
    # Check actual or fallback extension
    ext = p.suffix.lower()
    if ext in (".tif", ".tiff"):
        return GeoTiffReader(p)
    elif ext in (".h5", ".hdf5"):
        return Hdf5Reader(p)
    elif ext == ".npz":
        # Inspect npz keys
        data = np.load(p)
        if "chunks" in data:
            return Hdf5Reader(p)
        return GeoTiffReader(p)
    else:
        # Default try GeoTIFF
        return GeoTiffReader(p)
