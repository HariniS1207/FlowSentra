from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    """
    Input received by the FlowSentra intelligence engine.

    Field names must remain aligned with the backend API contract.
    """

    drain_id: str = Field(..., min_length=1)

    water_level_cm: float = Field(..., ge=0)

    flow_rate_lpm: float = Field(..., ge=0)

    rainfall: float = Field(..., ge=0)

    timestamp: datetime


class DrainFeatures(BaseModel):
    """
    Derived features used by the intelligence engine.
    """

    water_level_cm: float
    flow_rate_lpm: float
    rainfall: float

    water_level_change: float = 0.0
    flow_rate_change: float = 0.0

    water_level_rising: bool = False
    flow_rate_decreasing: bool = False

    water_level_rise_rate: float = 0.0
    flow_rate_change_rate: float = 0.0

    rainfall_level: str = "LOW"

    sensor_data_valid: bool = True


class DrainAnalysis(BaseModel):
    """
    Final intelligence output consumed by the backend/frontend.

    This structure intentionally matches the existing FlowSentra
    backend API contract.
    """

    drain_id: str

    health_score: int = Field(..., ge=0, le=100)

    condition: str

    probable_cause: str

    severity: str

    overflow_risk: int = Field(..., ge=0, le=100)

    sensor_confidence: int = Field(..., ge=0, le=100)

    maintenance_priority: str

    recommended_action: str


class IntelligenceResult(BaseModel):
    """
    Internal result containing the final analysis plus an explanation.

    The explanation is useful for the hackathon demo but does not
    need to be sent to the existing frontend contract yet.
    """

    analysis: DrainAnalysis

    explanation: str