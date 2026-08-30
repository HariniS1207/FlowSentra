from ai.models.schemas import SensorReading
from ai.services.intelligence_engine import analyze_drain


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


def test_complete_normal_analysis():

    previous = make_reading(10, 5, 0, 20)

    current = make_reading(10.5, 5.1, 0, 30)

    result = analyze_drain(
        current=current,
        history=[previous],
    )

    analysis = result.analysis

    assert analysis.drain_id == "D001"
    assert analysis.probable_cause == "NORMAL_DRAINAGE"
    assert analysis.condition == "NORMAL"
    assert analysis.severity == "LOW"
    assert analysis.maintenance_priority == "P3"

    assert 0 <= analysis.health_score <= 100
    assert 0 <= analysis.overflow_risk <= 100
    assert 0 <= analysis.sensor_confidence <= 100

    assert analysis.recommended_action
    assert result.explanation


def test_complete_partial_blockage_analysis():

    previous = make_reading(20, 3, 1, 20)

    current = make_reading(22, 2, 1, 30)

    result = analyze_drain(
        current=current,
        history=[previous],
    )

    analysis = result.analysis

    assert analysis.probable_cause == "PARTIAL_BLOCKAGE"
    assert analysis.condition == "WARNING"
    assert analysis.severity in ("MEDIUM", "HIGH")
    assert analysis.maintenance_priority == "P2"

    assert "blockage" in (
        analysis.recommended_action.lower()
        + result.explanation.lower()
    )


def test_complete_severe_blockage_analysis():

    previous = make_reading(35, 1.2, 1, 20)

    current = make_reading(40, 0.4, 1, 30)

    result = analyze_drain(
        current=current,
        history=[previous],
    )

    analysis = result.analysis

    assert analysis.probable_cause == "SEVERE_BLOCKAGE"
    assert analysis.condition == "CRITICAL"
    assert analysis.severity == "CRITICAL"
    assert analysis.maintenance_priority == "P1"

    assert analysis.health_score <= 30
    assert analysis.overflow_risk >= 70


def test_complete_heavy_rainfall_analysis():

    previous = make_reading(20, 5, 8, 20)

    current = make_reading(30, 8, 12, 30)

    result = analyze_drain(
        current=current,
        history=[previous],
    )

    analysis = result.analysis

    assert analysis.probable_cause == "HEAVY_RAINFALL"

    assert analysis.condition in (
        "NORMAL",
        "WARNING",
    )

    assert analysis.sensor_confidence >= 90


def test_complete_abnormal_flow_analysis():

    previous = make_reading(10, 1.0, 0, 20)

    current = make_reading(10, 0.5, 0, 30)

    result = analyze_drain(
        current=current,
        history=[previous],
    )

    analysis = result.analysis

    assert analysis.probable_cause == "ABNORMAL_FLOW"

    assert analysis.condition in (
        "NORMAL",
        "WARNING",
    )

    assert analysis.recommended_action