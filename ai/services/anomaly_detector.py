from ai.models.schemas import DrainFeatures


def detect_anomaly(features: DrainFeatures) -> bool:
    """
    Lightweight rule-based anomaly detector.

    This does NOT replace the drainage condition classifier.

    Its purpose is to identify unusual sensor behaviour that may
    require additional attention.

    Returns:
        True  -> unusual sensor pattern detected
        False -> no obvious anomaly detected
    """

    # ---------------------------------------------------------------
    # Extreme absolute values
    # ---------------------------------------------------------------

    if features.water_level_cm > 100:
        return True

    if features.flow_rate_lpm > 100:
        return True

    if features.rainfall > 100:
        return True

    # ---------------------------------------------------------------
    # Sudden water-level jump
    # ---------------------------------------------------------------

    if abs(features.water_level_change) >= 15:
        return True

    # ---------------------------------------------------------------
    # Sudden flow jump/drop
    # ---------------------------------------------------------------

    if abs(features.flow_rate_change) >= 20:
        return True

    # ---------------------------------------------------------------
    # Strong contradictory behaviour
    # ---------------------------------------------------------------

    if (
        features.water_level_change >= 5
        and features.flow_rate_change <= -1
        and features.rainfall < 5
    ):
        return True

    return False