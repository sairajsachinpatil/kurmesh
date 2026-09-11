import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterRequest(Payload):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)


class LoginRequest(Payload):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class VesselRequest(Payload):
    name: str = Field(min_length=1, max_length=200)
    vessel_type: str = Field(min_length=1, max_length=80)
    imo_number: str | None = Field(default=None, max_length=20)
    specifications: dict[str, Any] = Field(default_factory=dict)


class MissionCreateRequest(Payload):
    name: str = Field(min_length=1, max_length=200)
    vessel_id: uuid.UUID | None = None
    departure_at: datetime | None = None


class MissionUpdateRequest(Payload):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    vessel_id: uuid.UUID | None = None
    departure_at: datetime | None = None


class MissionTransitionRequest(Payload):
    state: Literal["DRAFT", "PLANNING", "ANALYZING", "ROUTES_AVAILABLE", "UNDER_REVIEW", "APPROVED", "REJECTED", "COMPLETED", "FAILED"]


class ConstraintRequest(Payload):
    constraint_type: str = Field(min_length=1, max_length=80)
    value: dict[str, Any]


class ReviewRequest(Payload):
    decision: Literal["RECOMMENDED", "NOT_RECOMMENDED", "NEEDS_CHANGES"]
    reason: str | None = Field(default=None, max_length=5000)


class ApprovalRequest(Payload):
    decision: Literal["APPROVED", "REJECTED"]
    reason: str | None = Field(default=None, max_length=5000)


class SimulationRequest(Payload):
    mission_id: uuid.UUID | None = None
    scenario: dict[str, Any]


class EnvironmentSourceCreateRequest(Payload):
    provider: str = Field(min_length=1, max_length=120)
    source: str = Field(min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EnvironmentSourceUpdateRequest(Payload):
    provider: str | None = Field(default=None, min_length=1, max_length=120)
    source: str | None = Field(default=None, min_length=1, max_length=200)
    url: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] | None = None


class PointLocation(Payload):
    longitude: float = Field(ge=-180, le=180)
    latitude: float = Field(ge=-90, le=90)


class EnvironmentObservationCreateRequest(Payload):
    source_id: uuid.UUID
    observation_type: str = Field(min_length=1, max_length=100)
    status: Literal["LIVE", "STALE", "UNAVAILABLE", "ERROR", "DEGRADED"]
    value: dict[str, Any]
    units: str = Field(min_length=1, max_length=64)
    quality: str | None = Field(default=None, max_length=64)
    resolution: str | None = Field(default=None, max_length=64)
    retrieved_at: datetime
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    location: PointLocation | None = None


class ModelVersionCreateRequest(Payload):
    name: str = Field(min_length=1, max_length=160)
    version: str = Field(min_length=1, max_length=80)
    status: str = Field(min_length=1, max_length=32)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelVersionUpdateRequest(Payload):
    status: str | None = Field(default=None, min_length=1, max_length=32)
    metadata: dict[str, Any] | None = None


class ModelArtifactCreateRequest(Payload):
    path: str = Field(min_length=1, max_length=2000)
    sha256: str = Field(pattern=r"^[a-fA-F0-9]{64}$")
    artifact_type: str = Field(min_length=1, max_length=80)


class PredictionCreateRequest(Payload):
    mission_id: uuid.UUID
    model_version_id: uuid.UUID
    status: Literal["PENDING", "FAILED", "MODEL_UNAVAILABLE"]
    input_provenance: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] | None = None
    reason: str | None = None
