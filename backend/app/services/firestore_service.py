from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore


# ============================================================
# FIREBASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
CREDENTIALS_DIR = BASE_DIR / "credentials"


def _find_credentials_file() -> Path:
    """Find the single Firebase service-account JSON file."""

    json_files = list(CREDENTIALS_DIR.glob("*.json"))

    if not json_files:
        raise FileNotFoundError(
            "No Firebase service-account JSON file found in "
            "backend/credentials/"
        )

    if len(json_files) > 1:
        raise RuntimeError(
            "Multiple Firebase credential files found. "
            "Keep only the active one."
        )

    return json_files[0]


def initialize_firestore():
    """Initialize Firebase Admin SDK and return Firestore client."""

    if not firebase_admin._apps:
        credential_path = _find_credentials_file()

        cred = credentials.Certificate(
            str(credential_path)
        )

        firebase_admin.initialize_app(cred)

    return firestore.client()


db = initialize_firestore()


# ============================================================
# LIVE MEMORY CACHE
# ============================================================
#
# The live dashboard uses these caches.
#
# This means:
#
# Arduino
#    ↓
# FastAPI
#    ↓
# Memory cache
#    ↓
# Dashboard / AI / Graph
#
# Firestore is NOT required for live monitoring.
# ============================================================

_latest_sensor_cache: dict[str, dict[str, Any]] = {}

_history_sensor_cache: dict[str, list[dict[str, Any]]] = {}


# ============================================================
# FIRESTORE BACKUP CONTROL
# ============================================================
#
# We only attempt a Firestore backup once every 30 seconds
# per drain.
#
# This greatly reduces Firestore writes compared with storing
# every Arduino reading.
# ============================================================

FIRESTORE_WRITE_INTERVAL_SECONDS = 30

_last_firestore_write: dict[str, datetime] = {}


# ============================================================
# STORE SENSOR READING
# ============================================================

def store_sensor_reading(reading: dict) -> str:
    """
    Process a new sensor reading.

    The live cache is updated FIRST.

    Firestore is used only as optional persistent backup.

    If Firestore is unavailable or quota is exceeded,
    live monitoring continues normally.
    """

    drain_id = reading["drain_id"]

    # --------------------------------------------------------
    # 1. BACKEND RECEPTION TIME
    # --------------------------------------------------------
    #
    # The Arduino timestamp may be invalid or 1970.
    # Therefore the backend creates the authoritative timestamp.
    #
    # --------------------------------------------------------

    received_at = datetime.now(timezone.utc)

    received_at_iso = received_at.isoformat()

    # --------------------------------------------------------
    # 2. CREATE NORMALIZED LIVE READING
    # --------------------------------------------------------

    cached_reading = {
        "drain_id": drain_id,

        "water_level_cm": float(
            reading["water_level_cm"]
        ),

        "flow_rate_lpm": float(
            reading["flow_rate_lpm"]
        ),

        "rainfall": float(
            reading["rainfall"]
        ),

        # Real backend reception time
        "timestamp": received_at_iso,

        # Keep created_at for compatibility
        "created_at": received_at_iso,
    }

    # --------------------------------------------------------
    # 3. UPDATE LATEST CACHE
    # --------------------------------------------------------

    _latest_sensor_cache[drain_id] = cached_reading.copy()

    # --------------------------------------------------------
    # 4. UPDATE HISTORY CACHE
    # --------------------------------------------------------

    if drain_id not in _history_sensor_cache:
        _history_sensor_cache[drain_id] = []

    _history_sensor_cache[drain_id].append(
        cached_reading.copy()
    )

    # Keep only the latest 50 live readings.
    if len(_history_sensor_cache[drain_id]) > 50:
        _history_sensor_cache[drain_id] = (
            _history_sensor_cache[drain_id][-50:]
        )

    # --------------------------------------------------------
    # 5. LOG LIVE DATA
    # --------------------------------------------------------

    print(
        f"Live cache updated: "
        f"{drain_id} | "
        f"Water={cached_reading['water_level_cm']:.1f} cm | "
        f"Flow={cached_reading['flow_rate_lpm']:.1f} L/min | "
        f"RainRaw={cached_reading['rainfall']:.0f}"
    )

    # --------------------------------------------------------
    # 6. OPTIONAL FIRESTORE BACKUP
    # --------------------------------------------------------

    now = received_at

    last_write = _last_firestore_write.get(drain_id)

    should_write = (
        last_write is None
        or (
            now - last_write
        ).total_seconds()
        >= FIRESTORE_WRITE_INTERVAL_SECONDS
    )

    if not should_write:
        print(
            f"Firestore backup skipped for {drain_id}"
        )

        return "memory-cache"

    # --------------------------------------------------------
    # 7. TRY FIRESTORE BACKUP
    # --------------------------------------------------------
    #
    # IMPORTANT:
    #
    # A Firestore failure MUST NOT affect the live system.
    #
    # --------------------------------------------------------

    try:

        reading_data = {
            "drain_id": drain_id,

            "water_level_cm": cached_reading[
                "water_level_cm"
            ],

            "flow_rate_lpm": cached_reading[
                "flow_rate_lpm"
            ],

            "rainfall": cached_reading[
                "rainfall"
            ],

            "timestamp": received_at,

            "created_at": received_at,
        }

        doc_ref = (
            db.collection("drains")
            .document(drain_id)
            .collection("readings")
            .document()
        )

        doc_ref.set(reading_data)

        _last_firestore_write[drain_id] = now

        print(
            f"Firestore backup written for {drain_id}"
        )

        return doc_ref.id

    except Exception as exc:

        print(
            "Firestore backup unavailable."
        )

        print(
            f"Firestore error: {exc}"
        )

        print(
            "Live monitoring continues using memory cache."
        )

        return "memory-cache"


# ============================================================
# GET LATEST SENSOR READING
# ============================================================

def get_latest_sensor_reading(
    drain_id: str,
) -> Optional[dict[str, Any]]:
    """
    Return the latest sensor reading from the live cache.

    NO Firestore read is performed here.

    This endpoint therefore remains available even when
    Firestore has reached its read quota.
    """

    cached_reading = _latest_sensor_cache.get(
        drain_id
    )

    if cached_reading is None:
        return None

    return cached_reading.copy()


# ============================================================
# GET SENSOR HISTORY
# ============================================================

def get_sensor_history(
    drain_id: str,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Return recent sensor readings from the live cache.

    NO Firestore read is performed here.

    The graph and AI engine therefore use the same live
    sensor history maintained by FastAPI.
    """

    cached_history = _history_sensor_cache.get(
        drain_id
    )

    if not cached_history:
        return []

    return [
        reading.copy()
        for reading in cached_history[-limit:]
    ]