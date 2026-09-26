import { apiGet, apiPost } from "./client";
import type { Mission, PaginatedResponse } from "./types";
export const getMissions = (signal?: AbortSignal) => apiGet<PaginatedResponse<Mission>>("/missions", { signal, authenticated: true });

export interface MissionCreatePayload {
  name: string;
  vessel_id: string;
  departure_at: string;
}

export const createMission = (payload: MissionCreatePayload) => apiPost<Mission>("/missions", payload, { authenticated: true });
