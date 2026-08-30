from ai.models.schemas import DrainFeatures


def clamp(value: float, minimum: float = 0, maximum: float = 100) -> int:
    """Keep confidence inside the 0-100 range."""
    return int(round(max(minimum, min(maximum, value))))


def calculate_sensor_confidence(
    features: DrainFeatures,
) -> int:
    """
    Estimate confidence in the current sensor measurements.

    Higher score means the measurements appear more plausible
    and internally consistent.

    Important:
    A rapid change is not automatically a sensor error.
    For example, heavy rainfall can legitimately cause a rapid
    increase in water level.

    This is a prototype confidence model for FlowSentra.
    """

    score = 100.0

    water = features.water_level_cm
    flow = features.flow_rate_lpm
    rainfall = features.rainfall

    water_change = features.water_level_change
    flow_change = features.flow_rate_change

    # ---------------------------------------------------------------
    # 1. Basic validity
    # ---------------------------------------------------------------

    if not features.sensor_data_valid:
        return 20

    # ---------------------------------------------------------------
    # 2. Absolute plausibility checks
    # ---------------------------------------------------------------

    if water > 100:
        score -= 25

    if flow > 100:
        score -= 20

    if rainfall > 100:
        score -= 20

    # ---------------------------------------------------------------
    # 3. Context-aware water-level change
    # ---------------------------------------------------------------
    #
    # A large water increase during heavy rainfall can be completely
    # legitimate. Therefore we do not heavily penalize it when:
    #
    #   rainfall is high
    #   AND flow is also increasing
    #
    # That pattern is actually consistent with rainfall-driven flow.
    # ---------------------------------------------------------------

    rainfall_supported_rise = (
        rainfall >= 10
        and water_change > 0
        and flow_change >= 0
    )

    if not rainfall_supported_rise:

        if abs(water_change) >= 15:
            score -= 25

        elif abs(water_change) >= 10:
            score -= 15

        elif abs(water_change) >= 5:
            score -= 7

    # ---------------------------------------------------------------
    # 4. Flow-rate change
    # ---------------------------------------------------------------

    if abs(flow_change) >= 20:
        score -= 20

    elif abs(flow_change) >= 10:
        score -= 12

    elif abs(flow_change) >= 5:
        score -= 5

    # ---------------------------------------------------------------
    # 5. Cross-sensor consistency
    # ---------------------------------------------------------------
    #
    # High rainfall + increasing water + increasing flow
    # is internally consistent.
    #
    # High rainfall + stagnant flow can be suspicious, because
    # rainfall-driven water accumulation would normally produce
    # some flow response.
    # ---------------------------------------------------------------

    if rainfall >= 10 and flow <= 0.2:
        score -= 5

    # ---------------------------------------------------------------
    # 6. Strongly contradictory pattern
    # ---------------------------------------------------------------
    #
    # Very rapidly rising water while flow is falling significantly
    # and rainfall is absent/low is much more suspicious.
    # This is relevant for blockage detection.
    # ---------------------------------------------------------------

    if (
        water_change >= 5
        and flow_change <= -1
        and rainfall < 5
    ):
        score -= 5

    return clamp(score)