from datetime import datetime

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    drain_id: str = Field(..., min_length=1)
    water_level_cm: float = Field(..., ge=0)
    flow_rate_lpm: float = Field(..., ge=0)
    rainfall: float
    timestamp: datetime