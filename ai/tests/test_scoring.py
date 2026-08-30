from ai.models.schemas import SensorReading

from ai.services.feature_engineering import build_features
from ai.services.condition_classifier import classify_condition
from ai.services.health_score import calculate_health_score
from ai.services.risk_engine import calculate_overflow_risk
from ai.services.severity import classify_severity


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

    return {
        "cause": cause,
        "health": health,
        "risk": risk,
        "severity": severity,
    }


def test_normal_scoring():

    previous = make_reading(10, 5, 0, 20)
    current = make_reading(10.5, 5.1, 0, 30)

    result = analyse(previous, current)

    assert result["cause"] == "NORMAL_DRAINAGE"
    assert result["health"] >= 70
    assert result["risk"] < 40
    assert result["severity"] == "LOW"


def test_partial_blockage_scoring():

    previous = make_reading(20, 3, 1, 20)
    current = make_reading(22, 2, 1, 30)

    result = analyse(previous, current)

    assert result["cause"] == "PARTIAL_BLOCKAGE"
    assert 40 <= result["health"] <= 65
    assert result["risk"] >= 40
    assert result["severity"] in ("MEDIUM", "HIGH")


def test_severe_blockage_scoring():

    previous = make_reading(35, 1.2, 1, 20)
    current = make_reading(40, 0.4, 1, 30)

    result = analyse(previous, current)

    assert result["cause"] == "SEVERE_BLOCKAGE"
    assert result["health"] <= 30
    assert result["risk"] >= 70
    assert result["severity"] == "CRITICAL"


def test_heavy_rainfall_scoring():

    previous = make_reading(20, 5, 8, 20)
    current = make_reading(30, 8, 12, 30)

    result = analyse(previous, current)

    assert result["cause"] == "HEAVY_RAINFALL"

    # Healthy flow during heavy rain should prevent
    # the drain from being treated like a severe blockage.
    assert result["health"] >= 55

    assert result["severity"] in ("LOW", "MEDIUM")


def test_abnormal_flow_scoring():

    previous = make_reading(10, 1.0, 0, 20)
    current = make_reading(10, 0.5, 0, 30)

    result = analyse(previous, current)

    assert result["cause"] == "ABNORMAL_FLOW"
    assert result["health"] <= 70