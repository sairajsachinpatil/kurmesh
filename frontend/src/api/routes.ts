import { apiGet } from "./client";
import type { PaginatedResponse, RouteCandidate } from "./types";
export const getRouteCandidates = (missionId: string, signal?: AbortSignal) => apiGet<PaginatedResponse<RouteCandidate>>(`/missions/${missionId}/route-candidates`, { signal, authenticated: true });
