/**
 * Mock GeoJSON spatial features for 1,000-acre demonstration farm and agricultural parcels.
 *
 * Coordinates located in UTM 43N / WGS-84 (~28.62 N, 77.10 E).
 * 1,000 acres ≈ 4.047 km² (approx 2.01 km x 2.01 km boundary polygon).
 */

import type { Feature, FeatureCollection, Polygon } from "geojson";

export interface FarmProperties {
  id: string;
  name: string;
  total_acres: number;
  crop_type: string;
  soil_type: string;
}

export interface ParcelProperties {
  parcel_id: string;
  name: string;
  acres: number;
  variety: string;
  planted_date: string;
}

export const MOCK_FARM_BOUNDARY: Feature<Polygon, FarmProperties> = {
  type: "Feature",
  properties: {
    id: "farm_001",
    name: "GreenValley Agri Parcel Alpha",
    total_acres: 1000.0,
    crop_type: "Winter Wheat",
    soil_type: "Clay Loam",
  },
  geometry: {
    type: "Polygon",
    coordinates: [
      [
        [77.0900, 28.6100],
        [77.1105, 28.6100],
        [77.1105, 28.6285],
        [77.0900, 28.6285],
        [77.0900, 28.6100],
      ],
    ],
  },
};

export const MOCK_PARCELS: FeatureCollection<Polygon, ParcelProperties> = {
  type: "FeatureCollection",
  features: [
    {
      type: "Feature",
      properties: {
        parcel_id: "p1",
        name: "North Parcel A",
        acres: 250.0,
        variety: "PBW-343",
        planted_date: "2025-11-15",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.0900, 28.61925],
            [77.10025, 28.61925],
            [77.10025, 28.6285],
            [77.0900, 28.6285],
            [77.0900, 28.61925],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        parcel_id: "p2",
        name: "North Parcel B",
        acres: 250.0,
        variety: "HD-2967",
        planted_date: "2025-11-18",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.10025, 28.61925],
            [77.1105, 28.61925],
            [77.1105, 28.6285],
            [77.10025, 28.6285],
            [77.10025, 28.61925],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        parcel_id: "p3",
        name: "South Parcel A (Outbreak Zone)",
        acres: 250.0,
        variety: "PBW-343",
        planted_date: "2025-11-15",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.0900, 28.6100],
            [77.10025, 28.6100],
            [77.10025, 28.61925],
            [77.0900, 28.61925],
            [77.0900, 28.6100],
          ],
        ],
      },
    },
    {
      type: "Feature",
      properties: {
        parcel_id: "p4",
        name: "South Parcel B",
        acres: 250.0,
        variety: "DBW-187",
        planted_date: "2025-11-20",
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.10025, 28.6100],
            [77.1105, 28.6100],
            [77.1105, 28.61925],
            [77.10025, 28.61925],
            [77.10025, 28.6100],
          ],
        ],
      },
    },
  ],
};
