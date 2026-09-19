import type { ApiErrorBody } from "./types";

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "/api/v1").replace(/\/$/, "");
const accessTokenKey = "kurmesh.accessToken";

export class ApiError extends Error {
  constructor(public readonly status: number, public readonly code?: string, message?: string) {
    super(message ?? "The API request failed.");
    this.name = "ApiError";
  }
}

export function hasAccessToken() {
  return Boolean(window.localStorage.getItem(accessTokenKey));
}

export async function apiGet<T>(path: string, options: { signal?: AbortSignal; authenticated?: boolean } = {}): Promise<T> {
  const token = options.authenticated ? window.localStorage.getItem(accessTokenKey) : null;
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    signal: options.signal,
  });
  const payload = await response.json().catch(() => undefined) as T | ApiErrorBody | undefined;
  if (!response.ok) {
    const error = payload as ApiErrorBody | undefined;
    throw new ApiError(response.status, error?.error?.code, error?.error?.message ?? response.statusText);
  }
  if (payload === undefined) throw new ApiError(response.status, "INVALID_RESPONSE", "The API returned an empty response.");
  return payload as T;
}
