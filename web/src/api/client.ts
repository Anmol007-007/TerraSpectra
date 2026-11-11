import { env } from "../utils/env";

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${env.apiBaseUrl}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorData = { code: "UNKNOWN_ERROR", message: response.statusText };
    try {
      errorData = await response.json();
    } catch {
      // Keep statusText fallback
    }
    throw new ApiError(response.status, errorData.code, errorData.message);
  }

  return response.json() as Promise<T>;
}
