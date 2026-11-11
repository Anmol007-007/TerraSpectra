# TerraSpectra Web GIS Dashboard

React 18 + TypeScript + Vite + Deck.gl 9 + Mapbox GL 3D satellite visualization platform.

## Features
- **3D Geospatial Viewer**: Deck.gl layers over Mapbox/MapLibre satellite imagery.
- **Hyperspectral Blight Forecasting**: Highlight 5-acre pre-symptomatic blight risk zones on 1,000-acre agricultural parcels.
- **Analytics Panel**: Acreage breakdown, spectral anomaly diagnostics.
- **Timeline Slider**: Historical playback of crop spectral changes.

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
