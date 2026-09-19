import { apiGet } from "./client";
import type { EnvironmentObservation, PaginatedResponse } from "./types";
export const getEnvironmentObservations = (signal?: AbortSignal) => apiGet<PaginatedResponse<EnvironmentObservation>>("/environment/observations", { signal, authenticated: true });
