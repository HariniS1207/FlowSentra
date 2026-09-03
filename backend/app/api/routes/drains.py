from typing import Any

from fastapi import APIRouter, HTTPException, status

from ai.models.schemas import SensorReading as AISensorReading
from ai.services.intelligence_engine import analyze_drain

from app.services.firestore_service import (
    get_latest_sensor_reading,
    get_sensor_history,
)


router = APIRouter(
    prefix="/api/v1/drains",
    tags=["Drains"],
)


def _normalize_rainfall(raw_rainfall: float) -> float:
    """
    Convert the raw rain-sensor ADC value from the hardware
    into the rainfall scale expected by the AI module.

    Current hardware behavior:
        ~1000 = NO RAIN
        ~300-400 = RAIN DETECTED

    AI rainfall scale:
        0.0 = no rain
        1.0 = low rain
        5.0 = moderate rain
        8.0 = heavy rain

    This is a prototype normalization and is NOT rainfall
    measured in millimetres.
    """

    # Dry / no rain
    if raw_rainfall >= 800:
        return 0.0

    # Light rain
    if raw_rainfall >= 600:
        return 1.0

    # Moderate rain
    if raw_rainfall >= 400:
        return 5.0

    # Heavy rain
    return 8.0


def _convert_to_ai_reading(
    reading: dict[str, Any],
) -> AISensorReading:
    """
    Convert a Firestore/backend sensor reading into the AI
    module's SensorReading model.

    Hardware-specific rainfall normalization is performed here.

    For AI trend analysis, prefer Firestore's created_at timestamp
    because it represents the actual time the backend received the
    reading. This avoids problems when multiple Arduino readings
    have identical sensor timestamps.
    """

    ai_timestamp = reading.get("created_at") or reading["timestamp"]

    return AISensorReading(
        drain_id=reading["drain_id"],
        water_level_cm=float(reading["water_level_cm"]),
        flow_rate_lpm=float(reading["flow_rate_lpm"]),
        rainfall=_normalize_rainfall(
            float(reading["rainfall"])
        ),
        timestamp=ai_timestamp,
    )


@router.get("/{drain_id}/latest")
def get_latest_reading(drain_id: str):

    reading = get_latest_sensor_reading(drain_id)

    if reading is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DRAIN_READING_NOT_FOUND",
                    "message": (
                        f"No sensor readings found for drain {drain_id}"
                    ),
                },
            },
        )

    return {
        "success": True,
        "drain_id": drain_id,
        "latest_reading": reading,
    }


@router.get("/{drain_id}/history")
def get_history(drain_id: str):

    readings = get_sensor_history(drain_id)

    if not readings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DRAIN_HISTORY_NOT_FOUND",
                    "message": (
                        f"No sensor readings found for drain {drain_id}"
                    ),
                },
            },
        )

    return {
        "success": True,
        "drain_id": drain_id,
        "readings": readings,
    }


@router.get("/{drain_id}/analysis")
def get_drain_analysis(drain_id: str):
    """
    Generate current drainage intelligence using the latest
    reading and recent sensor history.
    """

    # ---------------------------------------------------------------
    # 1. Get latest reading
    # ---------------------------------------------------------------

    latest = get_latest_sensor_reading(drain_id)

    if latest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": {
                    "code": "DRAIN_READING_NOT_FOUND",
                    "message": (
                        f"No sensor readings found for drain {drain_id}"
                    ),
                },
            },
        )

    # ---------------------------------------------------------------
    # 2. Get recent history
    # ---------------------------------------------------------------

    history = get_sensor_history(
        drain_id,
        limit=50,
    )

    # ---------------------------------------------------------------
    # 3. Convert backend data -> AI models
    # ---------------------------------------------------------------

    try:
        current_reading = _convert_to_ai_reading(latest)

        ai_history = [
            _convert_to_ai_reading(reading)
            for reading in history
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "AI_INPUT_CONVERSION_ERROR",
                    "message": (
                        "Failed to prepare sensor data for analysis"
                    ),
                },
            },
        ) from exc

    # ---------------------------------------------------------------
    # 4. Run intelligence engine
    # ---------------------------------------------------------------

    try:
        result = analyze_drain(
            current=current_reading,
            history=ai_history,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "DRAIN_ANALYSIS_ERROR",
                    "message": (
                        "Failed to analyse drain condition"
                    ),
                },
            },
        ) from exc

    # ---------------------------------------------------------------
    # 5. Return final intelligence
    # ---------------------------------------------------------------

    return {
        "success": True,
        "drain_id": drain_id,
        "analysis": result.analysis.model_dump(),
        "explanation": result.explanation,
    }