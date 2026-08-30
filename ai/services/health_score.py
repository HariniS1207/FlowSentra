from ai.models.schemas import DrainFeatures


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> int:
    """Keep a score inside the 0-100 range."""
    return int(round(max(minimum, min(maximum, value))))


def calculate_health_score(
    features: DrainFeatures,
    probable_cause: str,
) -> int:
    """
    Calculate the overall drainage health score.

    100 = very healthy drainage
    0   = extremely poor drainage

    The score considers:
    - water level
    - flow behaviour
    - water-level trend
    - probable drainage condition

    These are prototype thresholds for FlowSentra and must be
    calibrated against the actual hardware.
    """

    water = features.water_level_cm
    flow = features.flow_rate_lpm

    # Start from a healthy drain.
    score = 100.0

    # ---------------------------------------------------------------
    # WATER LEVEL PENALTY
    # ---------------------------------------------------------------

    if water >= 40:
        score -= 40
    elif water >= 30:
        score -= 25
    elif water >= 20:
        score -= 12
    elif water >= 15:
        score -= 5

    # ---------------------------------------------------------------
    # FLOW PENALTY
    # ---------------------------------------------------------------

    if flow <= 0.75:
        score -= 25
    elif flow <= 2:
        score -= 15
    elif flow < 3:
        score -= 7

    # ---------------------------------------------------------------
    # WATER LEVEL TREND
    # ---------------------------------------------------------------

    if features.water_level_change >= 3:
        score -= 15
    elif features.water_level_change >= 1:
        score -= 7

    # ---------------------------------------------------------------
    # FLOW TREND
    # ---------------------------------------------------------------

    if features.flow_rate_change <= -1:
        score -= 12
    elif features.flow_rate_change <= -0.5:
        score -= 6

    # ---------------------------------------------------------------
    # CONDITION-SPECIFIC ADJUSTMENT
    # ---------------------------------------------------------------

    if probable_cause == "SEVERE_BLOCKAGE":
        score = min(score, 30)

    elif probable_cause == "PARTIAL_BLOCKAGE":
        score = min(score, 65)

    elif probable_cause == "HEAVY_RAINFALL":
        # Heavy rainfall itself should not make a healthy drain
        # look like a blocked drain.
        score = max(score, 55)

    elif probable_cause == "ABNORMAL_FLOW":
        score = min(score, 70)

    elif probable_cause == "NORMAL_DRAINAGE":
        score = max(score, 70)

    return clamp(score)