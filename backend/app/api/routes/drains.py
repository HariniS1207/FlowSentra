from datetime import datetime
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


def _convert_to_ai_reading(reading: dict[str, Any]) -> AISensorReading:
    """
    Convert a Firestore/backend sensor reading into the AI module's
    SensorReading model.

    The field names remain unchanged.
    """

    return AISensorReading(
        drain_id=reading["drain_id"],
        water_level_cm=float(reading["water_level_cm"]),
        flow_rate_lpm=float(reading["flow_rate_lpm"]),
        rainfall=float(reading["rainfall"]),
        timestamp=reading["timestamp"],
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
    Generate current drainage intelligence using the latest reading
    and recent sensor history.
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
    # 3. Convert backend data → AI models
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
                    "message": "Failed to prepare sensor data for analysis",
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
                    "message": "Failed to analyse drain condition",
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