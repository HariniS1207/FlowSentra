from fastapi import APIRouter, HTTPException, status

from app.services.firestore_service import (
    get_latest_sensor_reading,
    get_sensor_history,
)


router = APIRouter(
    prefix="/api/v1/drains",
    tags=["Drains"],
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
                    "message": f"No sensor readings found for drain {drain_id}",
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
                    "message": f"No sensor readings found for drain {drain_id}",
                },
            },
        )

    return {
        "success": True,
        "drain_id": drain_id,
        "readings": readings,
    }