from typing import List, Optional

from ai.models.schemas import (
    DrainAnalysis,
    DrainFeatures,
    IntelligenceResult,
    SensorReading,
)

from ai.services.anomaly_detector import detect_anomaly
from ai.services.condition_classifier import classify_condition
from ai.services.confidence import calculate_sensor_confidence
from ai.services.feature_engineering import build_features
from ai.services.health_score import calculate_health_score
from ai.services.priority import calculate_maintenance_priority
from ai.services.recommendation import generate_recommended_action
from ai.services.risk_engine import calculate_overflow_risk
from ai.services.severity import classify_severity


def _get_previous_reading(
    current: SensorReading,
    history: Optional[List[SensorReading]],
) -> Optional[SensorReading]:
    """
    Find the most recent reading before the current reading.

    The history may be empty or unavailable.
    """

    if not history:
        return None

    previous_readings = [
        reading
        for reading in history
        if reading.timestamp < current.timestamp
    ]

    if not previous_readings:
        return None

    return max(
        previous_readings,
        key=lambda reading: reading.timestamp,
    )


def build_explanation(
    features: DrainFeatures,
    probable_cause: str,
    severity: str,
    overflow_risk: int,
) -> str:
    """
    Generate a concise, human-readable explanation for the
    intelligence result.
    """

    water = features.water_level_cm
    flow = features.flow_rate_lpm
    rainfall = features.rainfall

    water_change = features.water_level_change
    flow_change = features.flow_rate_change

    if probable_cause == "SEVERE_BLOCKAGE":
        return (
            f"Water level is high at {water:.1f} cm while flow is "
            f"very low at {flow:.1f} L/min. Water level changed by "
            f"{water_change:+.1f} cm while flow changed by "
            f"{flow_change:+.1f} L/min under {rainfall:.1f} rainfall, "
            f"indicating a probable severe flow restriction."
        )

    if probable_cause == "PARTIAL_BLOCKAGE":
        return (
            f"Water level is increasing ({water_change:+.1f} cm) "
            f"while flow is decreasing ({flow_change:+.1f} L/min) "
            f"with rainfall at {rainfall:.1f}, indicating possible "
            f"partial flow restriction or blockage."
        )

    if probable_cause == "HEAVY_RAINFALL":
        return (
            f"Rainfall is elevated at {rainfall:.1f} while water level "
            f"is {water:.1f} cm and flow is {flow:.1f} L/min. "
            f"The increased flow response is consistent with a "
            f"rainfall-driven drainage load."
        )

    if probable_cause == "ABNORMAL_FLOW":
        return (
            f"Flow is unusually low at {flow:.1f} L/min relative to "
            f"the observed drainage conditions, suggesting abnormal "
            f"flow behaviour or a sensor/path issue."
        )

    return (
        f"Water level is {water:.1f} cm, flow is {flow:.1f} L/min, "
        f"and rainfall is {rainfall:.1f}. Sensor behaviour is "
        f"consistent with normal drainage."
    )


def analyze_drain(
    current: SensorReading,
    history: Optional[List[SensorReading]] = None,
) -> IntelligenceResult:
    """
    Main FlowSentra intelligence entry point.

    Pipeline:

        Sensor Data
            ↓
        Feature Engineering
            ↓
        Anomaly Detection
            ↓
        Condition Classification
            ↓
        Health Score
            ↓
        Overflow Risk
            ↓
        Sensor Confidence
            ↓
        Severity
            ↓
        Maintenance Priority
            ↓
        Recommended Action
            ↓
        Final DrainAnalysis
    """

    # ---------------------------------------------------------------
    # 1. Find previous reading
    # ---------------------------------------------------------------

    previous = _get_previous_reading(
        current=current,
        history=history,
    )

    # ---------------------------------------------------------------
    # 2. Feature engineering
    # ---------------------------------------------------------------

    features = build_features(
        current=current,
        previous=previous,
    )

    # ---------------------------------------------------------------
    # 3. Anomaly detection
    # ---------------------------------------------------------------

    anomaly_detected = detect_anomaly(features)

    # ---------------------------------------------------------------
    # 4. Condition classification
    # ---------------------------------------------------------------

    probable_cause = classify_condition(features)

    # ---------------------------------------------------------------
    # 5. Health score
    # ---------------------------------------------------------------

    health_score = calculate_health_score(
        features=features,
        probable_cause=probable_cause,
    )

    # ---------------------------------------------------------------
    # 6. Overflow risk
    # ---------------------------------------------------------------

    overflow_risk = calculate_overflow_risk(features)

    # ---------------------------------------------------------------
    # 7. Sensor confidence
    # ---------------------------------------------------------------

    sensor_confidence = calculate_sensor_confidence(features)

    # ---------------------------------------------------------------
    # 8. Severity
    # ---------------------------------------------------------------

    severity = classify_severity(
        features=features,
        probable_cause=probable_cause,
        health_score=health_score,
        overflow_risk=overflow_risk,
    )

    # ---------------------------------------------------------------
    # 9. Maintenance priority
    # ---------------------------------------------------------------

    maintenance_priority = calculate_maintenance_priority(
        probable_cause=probable_cause,
        severity=severity,
        health_score=health_score,
        overflow_risk=overflow_risk,
        sensor_confidence=sensor_confidence,
    )

    # ---------------------------------------------------------------
    # 10. Recommended action
    # ---------------------------------------------------------------

    recommended_action = generate_recommended_action(
        probable_cause=probable_cause,
        severity=severity,
        overflow_risk=overflow_risk,
        sensor_confidence=sensor_confidence,
    )

    # ---------------------------------------------------------------
    # 11. Condition
    # ---------------------------------------------------------------

    if severity == "CRITICAL":
        condition = "CRITICAL"

    elif severity in ("MEDIUM", "HIGH"):
        condition = "WARNING"

    else:
        condition = "NORMAL"

    # ---------------------------------------------------------------
    # 12. Final analysis
    # ---------------------------------------------------------------

    analysis = DrainAnalysis(
        drain_id=current.drain_id,

        health_score=health_score,

        condition=condition,

        probable_cause=probable_cause,

        severity=severity,

        overflow_risk=overflow_risk,

        sensor_confidence=sensor_confidence,

        maintenance_priority=maintenance_priority,

        recommended_action=recommended_action,
    )

    # ---------------------------------------------------------------
    # 13. Explanation
    # ---------------------------------------------------------------

    explanation = build_explanation(
        features=features,
        probable_cause=probable_cause,
        severity=severity,
        overflow_risk=overflow_risk,
    )

    # Include anomaly information only when useful.
    if anomaly_detected and probable_cause == "NORMAL_DRAINAGE":
        explanation += (
            " An unusual sensor pattern was detected, so the "
            "reading should be monitored closely."
        )

    return IntelligenceResult(
        analysis=analysis,
        explanation=explanation,
    )