import json
import os
from datetime import datetime, timezone
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore


# Path to Firebase service-account credentials
BASE_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_DIR = BASE_DIR / "credentials"


def _find_credentials_file() -> Path:
    json_files = list(CREDENTIALS_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            "No Firebase service-account JSON file found in backend/credentials/"
        )

    if len(json_files) > 1:
        raise RuntimeError(
            "Multiple Firebase credential files found. Keep only the active one."
        )

    return json_files[0]


def initialize_firestore():
    """Initialize Firebase Admin SDK and return Firestore client."""

    if not firebase_admin._apps:
        credential_path = _find_credentials_file()
        cred = credentials.Certificate(str(credential_path))

        firebase_admin.initialize_app(cred)

    return firestore.client()


db = initialize_firestore()


def store_sensor_reading(reading: dict) -> str:
    """
    Store a sensor reading under:

    drains/{drain_id}/readings/{auto-generated-id}
    """

    drain_id = reading["drain_id"]

    reading_data = {
        "drain_id": drain_id,
        "water_level_cm": reading["water_level_cm"],
        "flow_rate_lpm": reading["flow_rate_lpm"],
        "rainfall": reading["rainfall"],
        "timestamp": reading["timestamp"],
        "created_at": datetime.now(timezone.utc),
    }

    doc_ref = (
        db.collection("drains")
        .document(drain_id)
        .collection("readings")
        .document()
    )

    doc_ref.set(reading_data)

    return doc_ref.id

def get_latest_sensor_reading(drain_id: str):
    """
    Retrieve the most recent sensor reading for a drain.
    """

    readings_ref = (
        db.collection("drains")
        .document(drain_id)
        .collection("readings")
    )

    docs = (
        readings_ref
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(1)
        .stream()
    )

    for doc in docs:
        data = doc.to_dict()

        # Firestore timestamp objects need conversion
        # before being returned as JSON.
        timestamp = data.get("timestamp")

        if hasattr(timestamp, "isoformat"):
            data["timestamp"] = timestamp.isoformat()

        if "created_at" in data:
            created_at = data["created_at"]

            if hasattr(created_at, "isoformat"):
                data["created_at"] = created_at.isoformat()

        return data

    return None

def get_sensor_history(drain_id: str, limit: int = 50):
    """
    Retrieve recent sensor readings for a drain.
    """

    readings_ref = (
        db.collection("drains")
        .document(drain_id)
        .collection("readings")
    )

    docs = (
        readings_ref
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )

    readings = []

    for doc in docs:
        data = doc.to_dict()

        timestamp = data.get("timestamp")
        if hasattr(timestamp, "isoformat"):
            data["timestamp"] = timestamp.isoformat()

        if "created_at" in data:
            created_at = data["created_at"]

            if hasattr(created_at, "isoformat"):
                data["created_at"] = created_at.isoformat()

        readings.append(data)

    # Return oldest → newest for charting
    readings.reverse()

    return readings