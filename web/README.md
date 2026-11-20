# TerraSpectra Web GIS Dashboard

React 18 + TypeScript + Vite + Deck.gl 9 + Mapbox GL 3D satellite visualization platform.

## Features
- **3D Geospatial Viewer**: Deck.gl 9 layers over Mapbox/MapLibre satellite imagery with 3D elevation pitch.
- **Hyperspectral Blight Forecasting**: Highlight 5-acre pre-symptomatic blight risk zones on 1,000-acre agricultural parcels 21 days before visible symptoms.
- **Interactive Pixel Inspector**: Real-time HUD inspecting individual 30m GSD cells, risk probabilities, severity, uncertainty, and estimated days to symptoms.
- **Ground Control Point (GCP) Calibration**: Visual validation markers and reticle crosshair verifying sub-pixel alignment ($\le 0.5$ pixel / $<15$m error).
- **Coordinate Readout HUD**: Live WGS84, raster pixel [R, C], and Web Mercator meters display.
- **Keyboard Shortcuts**:
  - `F`: Toggle 1,000-Acre Farm Boundary
  - `P`: Toggle Agricultural Parcels
  - `H`: Toggle Disease Risk Heatmap
  - `Z`: Toggle 5-Acre Blight Hotspot Zone
  - `G`: Toggle GCP Calibration Markers
  - `T`: Toggle 3D Topographic Terrain

## Quick Start
```bash
# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env.local
# Set VITE_MAPBOX_TOKEN (or leave blank to use open MapLibre style)

# 3. Start development server
npm run dev

# 4. Run tests
npm test
```
