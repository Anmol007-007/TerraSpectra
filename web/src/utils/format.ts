/**
 * Number and timestamp display formatting utilities.
 */

export function formatAcres(acres: number, decimals: number = 1): string {
  return `${acres.toFixed(decimals)} ac`;
}

export function formatPercent(fraction: number, decimals: number = 0): string {
  return `${(fraction * 100).toFixed(decimals)}%`;
}

export function formatDate(isoString: string): string {
  try {
    const d = new Date(isoString);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return isoString;
  }
}
