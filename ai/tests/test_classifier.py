from ai.models.schemas import SensorReading
from ai.services.feature_engineering import build_features
from ai.services.condition_classifier import classify_condition


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


def test_normal_drainage():
    previous = make_reading(10, 5, 0, 20)
    current = make_reading(10.5, 5.1, 0, 30)

    features = build_features(current, previous)

    assert classify_condition(features) == "NORMAL_DRAINAGE"


def test_partial_blockage():
    previous = make_reading(20, 3, 1, 20)
    current = make_reading(22, 2, 1, 30)

    features = build_features(current, previous)

    assert classify_condition(features) == "PARTIAL_BLOCKAGE"


def test_severe_blockage():
    previous = make_reading(35, 1.2, 1, 20)
    current = make_reading(40, 0.4, 1, 30)

    features = build_features(current, previous)

    assert classify_condition(features) == "SEVERE_BLOCKAGE"


def test_heavy_rainfall():
    previous = make_reading(20, 5, 8, 20)
    current = make_reading(30, 8, 12, 30)

    features = build_features(current, previous)

    assert classify_condition(features) == "HEAVY_RAINFALL"


def test_abnormal_flow():
    previous = make_reading(10, 1.0, 0, 20)
    current = make_reading(10, 0.5, 0, 30)

    features = build_features(current, previous)

    assert classify_condition(features) == "ABNORMAL_FLOW"