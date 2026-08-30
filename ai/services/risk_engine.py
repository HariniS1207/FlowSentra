from ai.models.schemas import DrainFeatures


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> int:
    """Keep risk inside the 0-100 range."""
    return int(round(max(minimum, min(maximum, value))))


def calculate_overflow_risk(features: DrainFeatures) -> int:
    """
    Estimate overflow risk using multiple sensor signals.

    Components:
        Water level       = 45%
        Water level trend = 25%
        Flow restriction  = 20%
        Rainfall          = 10%

    This is a prototype risk model for the hackathon.
    """

    water = features.water_level_cm
    flow = features.flow_rate_lpm
    water_change = features.water_level_change
    rainfall = features.rainfall

    # ---------------------------------------------------------------
    # 1. WATER LEVEL RISK — maximum 45 points
    # ---------------------------------------------------------------

    if water >= 40:
        water_risk = 45
    elif water >= 30:
        water_risk = 34
    elif water >= 20:
        water_risk = 22
    elif water >= 15:
        water_risk = 10
    else:
        water_risk = 3

    # ---------------------------------------------------------------
    # 2. WATER LEVEL TREND — maximum 25 points
    # ---------------------------------------------------------------

    if water_change >= 5:
        trend_risk = 25
    elif water_change >= 3:
        trend_risk = 20
    elif water_change >= 1:
        trend_risk = 10
    elif water_change > 0:
        trend_risk = 5
    else:
        trend_risk = 0

    # ---------------------------------------------------------------
    # 3. FLOW RESTRICTION — maximum 20 points
    # ---------------------------------------------------------------

    if flow <= 0.75:
        flow_risk = 20
    elif flow <= 2:
        flow_risk = 14
    elif flow < 3:
        flow_risk = 7
    else:
        flow_risk = 0

    # ---------------------------------------------------------------
    # 4. RAINFALL CONTRIBUTION — maximum 10 points
    # ---------------------------------------------------------------

    if rainfall >= 10:
        rainfall_risk = 10
    elif rainfall >= 5:
        rainfall_risk = 7
    elif rainfall > 0:
        rainfall_risk = 3
    else:
        rainfall_risk = 0

    total_risk = (
        water_risk
        + trend_risk
        + flow_risk
        + rainfall_risk
    )

    return clamp(total_risk)