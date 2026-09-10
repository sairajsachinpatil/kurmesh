import uuid
from datetime import UTC, datetime

from flask import Blueprint, g, jsonify, request
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.auth import ApiError, authenticate, issue_token, password_hash, password_matches, require_roles
from app.models import (Alert, AuditEvent, EnvironmentObservation, ModelVersion, Mission, MissionConstraint,
                        Prediction, ProvenanceRecord, Route, RouteApproval, RouteCandidate, RouteReview,
                        SimulationRun, User, Vessel)
from app.repositories import MissionRepository, Repository, UserRepository
from app.api.v1.schemas import (ApprovalRequest, ConstraintRequest, LoginRequest, MissionRequest,
                                MissionTransitionRequest, RegisterRequest, ReviewRequest, SimulationRequest,
                                VesselRequest)

api_blueprint = Blueprint("application", __name__)
TRANSITIONS = {"DRAFT": {"PLANNING", "FAILED"}, "PLANNING": {"ANALYZING", "FAILED"}, "ANALYZING": {"ROUTES_AVAILABLE", "FAILED"}, "ROUTES_AVAILABLE": {"UNDER_REVIEW", "FAILED"}, "UNDER_REVIEW": {"APPROVED", "REJECTED", "FAILED"}, "APPROVED": {"COMPLETED", "FAILED"}, "REJECTED": set(), "COMPLETED": set(), "FAILED": set()}


def body(schema):
    try:
        return schema.model_validate(request.get_json(silent=True) or {})
    except ValidationError as exc:
        raise ApiError("VALIDATION_ERROR", "Request validation failed", 422) from exc


def page(query, model, filters=()):
    limit = min(max(int(request.args.get("limit", 50)), 1), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    for predicate in filters:
        query = query.where(predicate)
    rows = list(g.db.scalars(query.limit(limit).offset(offset)))
    return jsonify({"items": [serialize(row) for row in rows], "limit": limit, "offset": offset})


def serialize(value):
    if isinstance(value, User): return {"id": str(value.id), "email": value.email, "is_active": value.is_active, "roles": [r.name for r in value.roles]}
    if isinstance(value, Vessel): return {"id": str(value.id), "name": value.name, "vessel_type": value.vessel_type, "imo_number": value.imo_number, "specifications": value.specifications}
    if isinstance(value, Mission): return {"id": str(value.id), "name": value.name, "state": value.state, "vessel_id": str(value.vessel_id) if value.vessel_id else None, "departure_at": value.departure_at.isoformat() if value.departure_at else None}
    if isinstance(value, MissionConstraint): return {"id": str(value.id), "mission_id": str(value.mission_id), "constraint_type": value.constraint_type, "value": value.value}
    if isinstance(value, Route): return {"id": str(value.id), "route_candidate_id": str(value.route_candidate_id), "status": value.status}
    if isinstance(value, RouteCandidate): return {"id": str(value.id), "mission_id": str(value.mission_id), "version": value.version, "status": "UNAVAILABLE", "reason": "Route geometry is only created by the routing subsystem"}
    if isinstance(value, Alert): return {"id": str(value.id), "mission_id": str(value.mission_id) if value.mission_id else None, "severity": value.severity, "status": value.status, "message": value.message}
    if isinstance(value, SimulationRun): return {"id": str(value.id), "mission_id": str(value.mission_id) if value.mission_id else None, "status": value.status, "is_simulation": True}
    if isinstance(value, AuditEvent): return {"id": str(value.id), "event_type": value.event_type, "entity_type": value.entity_type, "entity_id": str(value.entity_id) if value.entity_id else None, "occurred_at": value.occurred_at.isoformat()}
    if isinstance(value, ProvenanceRecord): return {"id": str(value.id), "entity_type": value.entity_type, "entity_id": str(value.entity_id), "source_type": value.source_type, "source_reference": value.source_reference, "details": value.details}
    if isinstance(value, ModelVersion): return {"id": str(value.id), "name": value.name, "version": value.version, "status": value.status, "metadata": value.metadata_json}
    if isinstance(value, Prediction): return {"id": str(value.id), "status": value.status, "reason": value.reason, "output": value.output}
    if isinstance(value, EnvironmentObservation): return {"id": str(value.id), "observation_type": value.observation_type, "status": value.status, "units": value.units, "retrieved_at": value.retrieved_at.isoformat()}
    raise TypeError(f"No serializer for {type(value)!r}")


def audit(event_type: str, entity_type: str, entity_id: uuid.UUID | None) -> None:
    actor = getattr(g, "current_user", None)
    g.db.add(AuditEvent(actor_id=actor.id if actor else None, event_type=event_type, entity_type=entity_type, entity_id=entity_id, payload={}))


def commit():
    try:
        g.db.commit()
    except IntegrityError:
        g.db.rollback()
        raise ApiError("CONFLICT", "The requested change conflicts with existing data", 409) from None


@api_blueprint.post("/auth/register")
def register():
    data = body(RegisterRequest)
    if UserRepository(g.db).by_email(str(data.email)):
        raise ApiError("CONFLICT", "Email is already registered", 409)
    user = User(email=str(data.email), password_hash=password_hash(data.password))
    g.db.add(user); commit(); audit("USER_REGISTERED", "User", user.id); commit()
    return jsonify({"user": serialize(user), "access_token": issue_token(user)}), 201


@api_blueprint.post("/auth/login")
def login():
    data = body(LoginRequest); user = UserRepository(g.db).by_email(str(data.email))
    if user is None or not password_matches(user.password_hash, data.password) or not user.is_active:
        raise ApiError("INVALID_CREDENTIALS", "Invalid credentials", 401)
    g.current_user = user; audit("USER_LOGIN", "User", user.id); commit()
    return jsonify({"access_token": issue_token(user), "token_type": "Bearer", "user": serialize(user)})


@api_blueprint.get("/users")
@require_roles("admin")
def users(): return page(select(User).order_by(User.created_at.desc()), User)


@api_blueprint.get("/users/me")
def current_user(): return jsonify(serialize(authenticate(g.db)))


@api_blueprint.route("/vessels", methods=["GET", "POST"])
def vessels():
    authenticate(g.db)
    if request.method == "GET": return page(select(Vessel).order_by(Vessel.created_at.desc()), Vessel)
    data = body(VesselRequest); vessel = Vessel(**data.model_dump()); g.db.add(vessel); commit(); audit("VESSEL_CREATED", "Vessel", vessel.id); commit()
    return jsonify(serialize(vessel)), 201


@api_blueprint.route("/vessels/<uuid:vessel_id>", methods=["GET", "PATCH", "DELETE"])
def vessel(vessel_id):
    authenticate(g.db); entity = g.db.get(Vessel, vessel_id)
    if entity is None: raise ApiError("NOT_FOUND", "Vessel not found", 404)
    if request.method == "GET": return jsonify(serialize(entity))
    if request.method == "DELETE": g.db.delete(entity); commit(); return "", 204
    for key, value in body(VesselRequest).model_dump().items(): setattr(entity, key, value)
    commit(); return jsonify(serialize(entity))


@api_blueprint.route("/missions", methods=["GET", "POST"])
def missions():
    user = authenticate(g.db)
    if request.method == "GET":
        query = select(Mission).order_by(Mission.created_at.desc())
        if state := request.args.get("state"): query = query.where(Mission.state == state)
        return page(query, Mission)
    data = body(MissionRequest); mission = Mission(**data.model_dump(), created_by_id=user.id); g.db.add(mission); commit(); audit("MISSION_CREATED", "Mission", mission.id); commit()
    return jsonify(serialize(mission)), 201


@api_blueprint.route("/missions/<uuid:mission_id>", methods=["GET", "PATCH", "DELETE"])
def mission(mission_id):
    user = authenticate(g.db); entity = MissionRepository(g.db).get(mission_id)
    if entity is None: raise ApiError("NOT_FOUND", "Mission not found", 404)
    if request.method == "GET": return jsonify(serialize(entity))
    if entity.created_by_id != user.id and "admin" not in {r.name for r in user.roles}: raise ApiError("FORBIDDEN", "Mission ownership is required", 403)
    if request.method == "DELETE": g.db.delete(entity); commit(); audit("MISSION_DELETED", "Mission", mission_id); commit(); return "", 204
    for key, value in body(MissionRequest).model_dump(exclude_unset=True).items(): setattr(entity, key, value)
    commit(); audit("MISSION_UPDATED", "Mission", mission_id); commit(); return jsonify(serialize(entity))


@api_blueprint.post("/missions/<uuid:mission_id>/transition")
def transition(mission_id):
    user = authenticate(g.db); entity = g.db.get(Mission, mission_id)
    if entity is None: raise ApiError("NOT_FOUND", "Mission not found", 404)
    requested = body(MissionTransitionRequest).state
    if requested == "APPROVED": raise ApiError("HUMAN_APPROVAL_REQUIRED", "Approve a reviewed route using the approval endpoint", 409)
    if requested not in TRANSITIONS[entity.state]: raise ApiError("INVALID_STATE_TRANSITION", f"Cannot transition from {entity.state} to {requested}", 409)
    entity.state = requested; g.current_user = user; audit("MISSION_TRANSITIONED", "Mission", entity.id); commit(); return jsonify(serialize(entity))


@api_blueprint.post("/missions/<uuid:mission_id>/constraints")
def mission_constraint(mission_id):
    authenticate(g.db)
    if g.db.get(Mission, mission_id) is None: raise ApiError("NOT_FOUND", "Mission not found", 404)
    data = body(ConstraintRequest); constraint = MissionConstraint(mission_id=mission_id, **data.model_dump()); g.db.add(constraint); commit(); return jsonify(serialize(constraint)), 201


@api_blueprint.get("/environment")
def environment():
    authenticate(g.db); return page(select(EnvironmentObservation).order_by(EnvironmentObservation.retrieved_at.desc()), EnvironmentObservation)


@api_blueprint.get("/predictions")
def predictions():
    authenticate(g.db); return page(select(Prediction).order_by(Prediction.created_at.desc()), Prediction)


@api_blueprint.get("/routes")
def routes():
    authenticate(g.db); return page(select(Route).order_by(Route.created_at.desc()), Route)


@api_blueprint.post("/routes/<uuid:route_id>/review")
def review_route(route_id):
    user = authenticate(g.db); route = g.db.get(Route, route_id)
    if route is None: raise ApiError("NOT_FOUND", "Route not found", 404)
    data = body(ReviewRequest); review = RouteReview(route_id=route_id, reviewer_id=user.id, **data.model_dump()); route.status = "UNDER_REVIEW"; g.db.add(review); audit("ROUTE_REVIEWED", "Route", route_id); commit()
    return jsonify({"id": str(review.id), "route_id": str(route_id), "decision": review.decision}), 201


@api_blueprint.post("/routes/<uuid:route_id>/approval")
@require_roles("operator", "admin")
def approve_route(route_id):
    route = g.db.get(Route, route_id)
    if route is None: raise ApiError("NOT_FOUND", "Route not found", 404)
    data = body(ApprovalRequest); user = g.current_user
    if data.decision == "APPROVED" and route.status != "UNDER_REVIEW": raise ApiError("ROUTE_NOT_UNDER_REVIEW", "A route must be reviewed before approval", 409)
    approval = RouteApproval(route_id=route_id, approver_id=user.id, **data.model_dump()); route.status = data.decision
    candidate = g.db.get(RouteCandidate, route.route_candidate_id); mission = g.db.get(Mission, candidate.mission_id) if candidate else None
    if mission: mission.state = data.decision
    g.db.add(approval); audit(f"ROUTE_{data.decision}", "Route", route_id); commit()
    return jsonify({"id": str(approval.id), "route_id": str(route_id), "decision": approval.decision}), 201


@api_blueprint.get("/alerts")
def alerts():
    authenticate(g.db); return page(select(Alert).order_by(Alert.created_at.desc()), Alert)


@api_blueprint.route("/simulation", methods=["GET", "POST"])
def simulation():
    authenticate(g.db)
    if request.method == "GET": return page(select(SimulationRun).order_by(SimulationRun.created_at.desc()), SimulationRun)
    data = body(SimulationRequest); run = SimulationRun(**data.model_dump(), status="PENDING", is_simulation=True); g.db.add(run); audit("SIMULATION_REQUESTED", "SimulationRun", run.id); commit()
    return jsonify(serialize(run)), 202


@api_blueprint.get("/provenance")
def provenance():
    authenticate(g.db); return page(select(ProvenanceRecord).order_by(ProvenanceRecord.created_at.desc()), ProvenanceRecord)


@api_blueprint.get("/models")
def models():
    authenticate(g.db); return page(select(ModelVersion).order_by(ModelVersion.created_at.desc()), ModelVersion)


@api_blueprint.get("/audit")
@require_roles("admin")
def audit_events(): return page(select(AuditEvent).order_by(AuditEvent.occurred_at.desc()), AuditEvent)
