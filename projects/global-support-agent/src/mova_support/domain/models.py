from __future__ import annotations

from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DiagnosisOutcome(StrEnum):
    NEED_MORE_EVIDENCE = "need_more_evidence"
    SELF_SERVICE = "self_service"
    HUMAN_REVIEW = "human_review"
    RESOLVED = "resolved"


class DeviceIdentity(BaseModel):
    category: str = "robot_vacuum"
    model: str
    region: str | None = None
    serial_number: str | None = None
    firmware_version: str | None = None
    app_version: str | None = None


class UserContext(BaseModel):
    locale: str = "en-US"
    country: str = "US"
    channel: str = "web"
    device_log_consent: bool = False


class Symptom(BaseModel):
    code: str
    original_text: str
    severity: RiskLevel = RiskLevel.LOW


class UnderstandingResult(BaseModel):
    language: str
    intent: str = "device_support"
    sentiment: str = "neutral"
    symptom_codes: list[str] = Field(default_factory=list)
    normalized_problem: str
    missing_information: list[str] = Field(default_factory=list)
    out_of_taxonomy: bool = False
    proposed_symptom_label: str | None = None
    confidence: float = Field(default=0, ge=0, le=1)
    source: str = "heuristic"


class Hypothesis(BaseModel):
    cause_code: str
    label: str
    confidence: float = Field(ge=0, le=1)
    supporting_evidence: list[str] = Field(default_factory=list)


class DiagnosticStep(BaseModel):
    step_id: str
    instruction: str
    purpose: str
    risk: RiskLevel = RiskLevel.LOW


class SafetyDecision(BaseModel):
    risk: RiskLevel
    requires_human: bool
    matched_rules: list[str] = Field(default_factory=list)
    user_message: str | None = None


class DiagnosisRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    locale: str = "en-US"
    country: str = Field(default="US", min_length=2, max_length=2)
    channel: str = "web"
    device_log_consent: bool = False
    device: DeviceIdentity
    session_id: UUID | None = None


class DiagnosisResponse(BaseModel):
    request_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    language: str
    intent: str
    sentiment: str
    normalized_problem: str
    understanding_source: str
    understanding_confidence: float = Field(ge=0, le=1)
    symptoms: list[Symptom]
    safety: SafetyDecision
    hypotheses: list[Hypothesis]
    next_step: DiagnosticStep | None = None
    outcome: DiagnosisOutcome
    reply: str
    clarifying_question: str | None = None
    suggested_replies: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    human_ticket_id: str | None = None
