from typing import Optional

from ai.models.schemas import SensorReading, DrainFeatures


def calculate_change(current: float, previous: Optional[float]) -> float:
    """
    Calculate the difference between the current and previous reading.

    If there is no previous reading, return 0.
    """

    if previous is None:
        return 0.0

    return current - previous


def classify_rainfall(rainfall: float) -> str:
    """
    Prototype rainfall classification.

    These thresholds are intentionally simple and are meant
    for hackathon prototype calibration, not real-world
    meteorological classification.
    """

    if rainfall <= 0:
        return "NONE"

    if rainfall < 5:
        return "LOW"

    if rainfall < 10:
        return "MODERATE"

    return "HIGH"


def build_features(
    current: SensorReading,
    previous: Optional[SensorReading] = None,
) -> DrainFeatures:
    """
    Convert raw sensor readings into derived intelligence features.
    """

    water_level_change = calculate_change(
        current.water_level_cm,
        previous.water_level_cm if previous else None,
    )

    flow_rate_change = calculate_change(
        current.flow_rate_lpm,
        previous.flow_rate_lpm if previous else None,
    )

    # Time difference in minutes.
    time_difference_minutes = 0.0

    if previous is not None:
        time_difference_seconds = (
            current.timestamp - previous.timestamp
        ).total_seconds()

        if time_difference_seconds > 0:
            time_difference_minutes = time_difference_seconds / 60.0

    # Calculate rate of change only when a valid time interval exists.
    if time_difference_minutes > 0:
        water_level_rise_rate = (
            water_level_change / time_difference_minutes
        )

        flow_rate_change_rate = (
            flow_rate_change / time_difference_minutes
        )
    else:
        water_level_rise_rate = 0.0
        flow_rate_change_rate = 0.0

    return DrainFeatures(
        water_level_cm=current.water_level_cm,
        flow_rate_lpm=current.flow_rate_lpm,
        rainfall=current.rainfall,

        water_level_change=water_level_change,
        flow_rate_change=flow_rate_change,

        water_level_rising=water_level_change > 0,
        flow_rate_decreasing=flow_rate_change < 0,

        water_level_rise_rate=water_level_rise_rate,
        flow_rate_change_rate=flow_rate_change_rate,

        rainfall_level=classify_rainfall(current.rainfall),

        sensor_data_valid=True,
    )