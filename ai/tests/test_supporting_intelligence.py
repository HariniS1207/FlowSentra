from ai.models.schemas import SensorReading

from ai.services.feature_engineering import build_features
from ai.services.condition_classifier import classify_condition
from ai.services.health_score import calculate_health_score
from ai.services.risk_engine import calculate_overflow_risk
from ai.services.severity import classify_severity
from ai.services.confidence import calculate_sensor_confidence
from ai.services.priority import calculate_maintenance_priority
from ai.services.recommendation import generate_recommended_action


def make_reading(
    water: float,
    flow: float,
    rainfall: float,
    minute: int,
) -> SensorReading:

    return SensorReading(
        drain_id="D001",
        water_level_cm=water,
        flow_rate_lpm=flow,
        rainfall=rainfall,
        timestamp=f"2026-08-29T10:{minute:02d}:00Z",
    )


def analyse(previous, current):

    features = build_features(current, previous)

    cause = classify_condition(features)

    health = calculate_health_score(
        features,
        cause,
    )

    risk = calculate_overflow_risk(features)

    severity = classify_severity(
        features,
        cause,
        health,
        risk,
    )

    confidence = calculate_sensor_confidence(features)

    priority = calculate_maintenance_priority(
        cause,
        severity,
        health,
        risk,
        confidence,
    )

    action = generate_recommended_action(
        cause,
        severity,
        risk,
        confidence,
    )

    return {
        "cause": cause,
        "health": health,
        "risk": risk,
        "severity": severity,
        "confidence": confidence,
        "priority": priority,
        "action": action,
    }


def test_normal_intelligence():

    previous = make_reading(10, 5, 0, 20)
    current = make_reading(10.5, 5.1, 0, 30)

    result = analyse(previous, current)

    assert result["cause"] == "NORMAL_DRAINAGE"
    assert result["health"] >= 70
    assert result["risk"] < 40
    assert result["severity"] == "LOW"
    assert result["confidence"] >= 90
    assert result["priority"] == "P3"
    assert "routine monitoring" in result["action"].lower()


def test_partial_blockage_intelligence():

    previous = make_reading(20, 3, 1, 20)
    current = make_reading(22, 2, 1, 30)

    result = analyse(previous, current)

    assert result["cause"] == "PARTIAL_BLOCKAGE"
    assert result["health"] <= 65
    assert result["risk"] >= 40
    assert result["severity"] in ("MEDIUM", "HIGH")
    assert result["priority"] == "P2"
    assert "inspect" in result["action"].lower()


def test_severe_blockage_intelligence():

    previous = make_reading(35, 1.2, 1, 20)
    current = make_reading(40, 0.4, 1, 30)

    result = analyse(previous, current)

    assert result["cause"] == "SEVERE_BLOCKAGE"
    assert result["health"] <= 30
    assert result["risk"] >= 70
    assert result["severity"] == "CRITICAL"
    assert result["confidence"] >= 90
    assert result["priority"] == "P1"
    assert "immediate" in result["action"].lower()


def test_heavy_rainfall_intelligence():

    previous = make_reading(20, 5, 8, 20)
    current = make_reading(30, 8, 12, 30)

    result = analyse(previous, current)

    assert result["cause"] == "HEAVY_RAINFALL"
    assert result["health"] >= 55
    assert result["confidence"] >= 90
    assert result["priority"] in ("P2", "P3")


def test_abnormal_flow_intelligence():

    previous = make_reading(10, 1.0, 0, 20)
    current = make_reading(10, 0.5, 0, 30)

    result = analyse(previous, current)

    assert result["cause"] == "ABNORMAL_FLOW"
    assert result["health"] <= 70
    assert result["priority"] in ("P2", "P3")


def test_low_confidence():

    previous = make_reading(20, 10, 0, 20)
    current = make_reading(40, 30, 0, 30)

    features = build_features(current, previous)

    confidence = calculate_sensor_confidence(features)

    assert confidence < 90