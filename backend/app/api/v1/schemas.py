import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RegisterRequest(Payload):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class LoginRequest(RegisterRequest):
    pass


class VesselRequest(Payload):
    name: str = Field(min_length=1, max_length=200)
    vessel_type: str = Field(min_length=1, max_length=80)
    imo_number: str | None = Field(default=None, max_length=20)
    specifications: dict[str, Any] = Field(default_factory=dict)


class MissionRequest(Payload):
    name: str = Field(min_length=1, max_length=200)
    vessel_id: uuid.UUID | None = None
    departure_at: datetime | None = None


class MissionTransitionRequest(Payload):
    state: Literal["DRAFT", "PLANNING", "ANALYZING", "ROUTES_AVAILABLE", "UNDER_REVIEW", "APPROVED", "REJECTED", "COMPLETED", "FAILED"]


class ConstraintRequest(Payload):
    constraint_type: str = Field(min_length=1, max_length=80)
    value: dict[str, Any]


class ReviewRequest(Payload):
    decision: str = Field(min_length=1, max_length=32)
    reason: str | None = Field(default=None, max_length=5000)


class ApprovalRequest(Payload):
    decision: Literal["APPROVED", "REJECTED"]
    reason: str | None = Field(default=None, max_length=5000)


class SimulationRequest(Payload):
    mission_id: uuid.UUID | None = None
    scenario: dict[str, Any]
