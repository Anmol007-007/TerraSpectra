# 07 — API Specification (FastAPI, prefix `/v1`)
| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | liveness + device info |
| GET | `/version` | app/model versions |
| GET | `/v1/models` | list loaded models |
| GET | `/v1/scenes` | list catalog scenes (paginated) |
| GET | `/v1/scenes/{scene_id}` | metadata + bounds |
| GET | `/v1/scenes/{scene_id}/timeline` | acquisitions + mean spectral health per date |
| POST | `/v1/scenes/upload` | upload GeoTIFF/HDF5 (size/type limits) |
| POST | `/v1/predict` | start async prediction `{scene_id, model_id?, horizon_days=21, tile_size=256, overlap=32, threshold=0.5}` → `202 {job_id}` |
| POST | `/v1/predict/tile` | synchronous single tile inference (debug) |
| GET | `/v1/jobs/{job_id}` | status: queued/running/succeeded/failed/cancelled + progress |
| DELETE | `/v1/jobs/{job_id}` | cancel |
| GET | `/v1/jobs/{job_id}/result` | heatmap + zones + analytics |
| GET | `/v1/jobs/{job_id}/zones` | GeoJSON FeatureCollection |
| GET | `/v1/scenes/{scene_id}/analytics` | acreage at risk + anomalies |
| GET | `/metrics` | Prometheus |
## Result JSON (the frontend contract; also used by mocks)
```json
{
  "scene_id": "farm_001", "model_version": "0.3.0", "acquired": "2026-06-01", "horizon_days": 21,
  "crs": "EPSG:4326", "gsd_m": 30, "origin": [77.1000, 28.6200], "cell_size_deg": [0.000285, 0.000285],
  "grid": {"rows": 67, "cols": 67,
           "risk": [[0.01, 0.02]], "severity": [[0.0, 0.1]], "uncertainty": [[0.05, 0.04]], "state": [[0, 1]]},
  "zones": {"type": "FeatureCollection", "features": [{"type": "Feature",
      "geometry": {"type": "Polygon", "coordinates": []},
      "properties": {"zone_id": "z1", "area_acres": 5.1, "mean_risk": 0.91, "lead_time_days": 21,
                     "disease": "fungal_blight", "recommended_action": "Targeted fungicide application"}}]},
  "analytics": {"total_acres": 1000, "acres_at_risk": 5.1, "acres_by_state": {"healthy": 990.2, "stressed": 4.7, "diseased": 5.1},
      "anomalies": [{"id": "chl_drop", "label": "Chlorophyll decline", "wavelength_nm": 680, "delta": -0.12, "severity": "high"}]}
}
```
Errors: `{ "error": {"code": "SCENE_NOT_FOUND", "message": "...", "request_id": "..."} }` with proper HTTP codes (400/404/413/422/429/500).
## Tiling algorithm
1. Compute tile grid: stride = tile − overlap; pad edges by reflection.
2. Stream windows via Rasterio (never full read); preprocess with training stats + PCA.
3. Batch tiles to GPU; dynamic batch size; on OOM halve batch and retry.
4. Multiply each tile output by a 2D Hann window; accumulate `sum(w*out)` and `sum(w)` in memmaps.
5. Normalise by weight sum → seamless raster; write GeoTIFF + extract zones with `rasterio.features.shapes`.
Invariant: tiled == full inference within 1e-3 on small scenes.
