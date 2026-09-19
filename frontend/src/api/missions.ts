import { apiGet } from "./client";
import type { Mission, PaginatedResponse } from "./types";
export const getMissions = (signal?: AbortSignal) => apiGet<PaginatedResponse<Mission>>("/missions", { signal, authenticated: true });
