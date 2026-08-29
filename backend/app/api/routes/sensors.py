import logging
from fastapi import APIRouter, HTTPException, status

from app.models.sensor import SensorReading
from app.services.firestore_service import store_sensor_reading

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/v1/sensors",
    tags=["Sensors"],
)


@router.post("/readings", status_code=status.HTTP_201_CREATED)
def receive_sensor_reading(reading: SensorReading):
    try:
        reading_id = store_sensor_reading(
            reading.model_dump(mode="json")
        )

        logger.info(
            "Sensor reading stored successfully: drain_id=%s, reading_id=%s",
            reading.drain_id,
            reading_id,
        )


        return {
            "success": True,
            "message": "Sensor reading received",
            "drain_id": reading.drain_id,
        }

    except Exception as exc:
        logger.exception(
            "Failed to store sensor reading for drain_id=%s",
            reading.drain_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "SENSOR_STORAGE_ERROR",
                    "message": "Failed to store sensor reading",
                },
            },
        ) from exc