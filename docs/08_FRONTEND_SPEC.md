# 08 — Frontend Specification (React + TS + Deck.gl + Mapbox)
## Screen layout
Header (logo, scene selector, model selector, Run prediction, theme toggle) · Left sidebar (layers, opacity, thresholds) · Centre 3D map · Right analytics panel (KPIs, acreage chart, anomalies) · Bottom timeline slider (play/pause, speed, compare).
## Map & layers (Deck.gl via `@deck.gl/mapbox` overlay or `DeckGL` + `react-map-gl`)
- Basemap: Mapbox satellite-streets (fallback MapLibre) + terrain (3D exaggeration slider).
- `farmBoundary` GeoJsonLayer (outline), `parcels` GeoJsonLayer, `heatmap` (GridCellLayer/ColumnLayer; colour scale green→yellow→red by risk, opacity slider, optional extrusion), `zones` PolygonLayer (red fill, pulsing outline, labels), `uncertainty` (toggle).
- Picking: hover tooltip (risk, severity, state, lat/lon, mini spectral signature), click selects zone → fly-to + details card (area acres, lead time, recommended action).
## State (Zustand slices)
`mapSlice` (viewState, terrain), `layerSlice` (visibility, opacity, thresholds), `sceneSlice` (sceneId, date), `jobSlice` (jobId, status), `uiSlice` (theme, panels).
## API layer
`api/client.ts` fetch wrapper (timeout, retries, error mapping) · zod schemas mirror `07_API_SPEC.md` · `VITE_USE_MOCKS=true` serves `api/mocks/*.json` via MSW · react-query hooks `useScenes, useScene, usePredict, useJob, useResult, useTimeline`.
## Utilities
`geo.ts` (pixel↔lon/lat, fitBounds, cell polygons), `acres.ts` (m²↔acres, cells→acres), `color.ts` (risk scale), `format.ts`.
## GIS validation (Mid-Project)
Known GCP fixtures (pixel→lonlat) shared with backend tests; debug overlay shows GCP markers + crosshair; test asserts overlay corner coords match backend bounds within 1e-6 deg.
## UX/quality
Responsive, dark mode, keyboard accessible (axe clean), loading skeletons, error boundary, export PNG/CSV, print style, lazy-loaded heavy layers, Lighthouse perf >= 85.
