from enum import Enum

from pydantic import BaseModel, Field


class Condition(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MaintenancePriority(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class DrainAnalysis(BaseModel):
    drain_id: str
    health_score: int = Field(..., ge=0, le=100)
    condition: Condition
    probable_cause: str
    severity: Severity
    overflow_risk: int = Field(..., ge=0, le=100)
    sensor_confidence: int = Field(..., ge=0, le=100)
    maintenance_priority: MaintenancePriority
    recommended_action: str