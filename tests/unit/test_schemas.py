"""Unit tests for domain schemas and Pydantic validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from terraspectra.core.schemas import (
    AnalyticsSummary,
    Anomaly,
    GeoBounds,
    Job,
    JobStatus,
    PixelState,
    RiskZone,
    TileSpec,
)


def test_geo_bounds_validation() -> None:
    """Test GeoBounds construction and coordinate tuple."""
    bounds = GeoBounds(west=77.10, south=28.62, east=77.15, north=28.67)
    assert bounds.crs == "EPSG:4326"
    assert bounds.tuple == (77.10, 28.62, 77.15, 28.67)


def test_pixel_state_enum() -> None:
    """Test PixelState int enum values."""
    assert PixelState.HEALTHY == 0
    assert PixelState.PRE_SYMPTOMATIC == 1
    assert PixelState.VISIBLY_DISEASED == 2
    assert PixelState.INVALID == 255


def test_tile_spec_validation() -> None:
    """Test TileSpec window attributes."""
    tile = TileSpec(row_start=0, col_start=0, height=256, width=256, pad_bottom=16)
    assert tile.height == 256
    assert tile.pad_bottom == 16


def test_job_status_and_model() -> None:
    """Test Job model defaults and status changes."""
    job = Job(job_id="job-123", scene_id="farm_001", created_at="2026-06-01T10:00:00Z")
    assert job.status == JobStatus.QUEUED
    assert job.progress == 0.0


def test_risk_zone_validation() -> None:
    """Test RiskZone creation and validation constraints."""
    zone = RiskZone(
        zone_id="z1",
        area_acres=5.1,
        mean_risk=0.88,
        geometry={"type": "Polygon", "coordinates": []},
    )
    assert zone.area_acres == 5.1
    assert zone.lead_time_days == 21

    with pytest.raises(ValidationError):
        RiskZone(
            zone_id="z2",
            area_acres=1.0,
            mean_risk=1.5,  # Exceeds max 1.0
            geometry={},
        )


def test_analytics_summary() -> None:
    """Test AnalyticsSummary with Anomaly models."""
    anomaly = Anomaly(
        id="chl_drop", label="Chlorophyll decline", wavelength_nm=680.0, delta=-0.14
    )
    summary = AnalyticsSummary(
        total_acres=1000.0,
        acres_at_risk=5.1,
        acres_by_state={"healthy": 990.2, "stressed": 4.7, "diseased": 5.1},
        anomalies=[anomaly],
    )
    assert summary.acres_at_risk == 5.1
    assert len(summary.anomalies) == 1
