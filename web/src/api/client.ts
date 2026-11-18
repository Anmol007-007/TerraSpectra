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

export interface ApiClientOptions extends RequestInit {
  timeoutMs?: number;
  retries?: number;
  retryDelayMs?: number;
}

export async function apiClient<T>(
  endpoint: string,
  options?: ApiClientOptions,
): Promise<T> {
  const url = `${env.apiBaseUrl}${endpoint}`;
  const timeoutMs = options?.timeoutMs ?? 10000;
  const maxRetries = options?.retries ?? 2;
  const retryDelay = options?.retryDelayMs ?? 300;

  let attempt = 0;

  while (attempt <= maxRetries) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          "Content-Type": "application/json",
          ...options?.headers,
        },
      });

      clearTimeout(timer);

      if (!response.ok) {
        let errorData = { code: "UNKNOWN_ERROR", message: response.statusText };
        try {
          errorData = (await response.json()) as { code: string; message: string };
        } catch {
          // Keep statusText fallback
        }
        throw new ApiError(response.status, errorData.code, errorData.message);
      }

      return (await response.json()) as T;
    } catch (err: unknown) {
      clearTimeout(timer);
      attempt++;

      if (attempt > maxRetries) {
        if (err instanceof ApiError) {
          throw err;
        }
        if (err instanceof Error && err.name === "AbortError") {
          throw new ApiError(408, "TIMEOUT", `Request to ${endpoint} timed out after ${timeoutMs}ms`);
        }
        throw new ApiError(0, "NETWORK_ERROR", err instanceof Error ? err.message : String(err));
      }

      // Exponential backoff wait
      await new Promise((resolve) => setTimeout(resolve, retryDelay * Math.pow(2, attempt - 1)));
    }
  }

  throw new ApiError(0, "NETWORK_ERROR", "Request failed after all retries");
}
