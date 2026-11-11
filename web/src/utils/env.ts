/**
 * Typed environment variables helper with safe defaults.
 */

export interface AppEnv {
  apiBaseUrl: string;
  mapboxToken: string;
  useMocks: boolean;
  basemap: "mapbox" | "maplibre";
}

export function getAppEnv(): AppEnv {
  return {
    apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
    mapboxToken: import.meta.env.VITE_MAPBOX_TOKEN || "",
    useMocks: import.meta.env.VITE_USE_MOCKS === "true",
    basemap: (import.meta.env.VITE_BASEMAP as "mapbox" | "maplibre") || "maplibre",
  };
}

export const env = getAppEnv();
