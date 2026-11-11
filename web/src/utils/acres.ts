import { ACRES_PER_M2, M2_PER_ACRE, GSD_METRES } from "./constants";

export function m2ToAcres(areaM2: number): number {
  return areaM2 * ACRES_PER_M2;
}

export function acresToM2(areaAcres: number): number {
  return areaAcres * M2_PER_ACRE;
}

export function pixelsToAcres(pixelCount: number, gsdM: number = GSD_METRES): number {
  return m2ToAcres(pixelCount * gsdM * gsdM);
}

export function acresToPixels(areaAcres: number, gsdM: number = GSD_METRES): number {
  return acresToM2(areaAcres) / (gsdM * gsdM);
}
