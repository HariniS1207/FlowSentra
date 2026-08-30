from ai.models.schemas import DrainFeatures


# ---------------------------------------------------------------------------
# Prototype thresholds
# ---------------------------------------------------------------------------
# These values are intentionally configurable and are meant for prototype
# calibration against the actual FlowSentra hardware.
#
# They are NOT universal real-world drainage thresholds.
# ---------------------------------------------------------------------------

WATER_LEVEL_WARNING_CM = 20.0
WATER_LEVEL_HIGH_CM = 30.0
WATER_LEVEL_CRITICAL_CM = 40.0

FLOW_LOW_LPM = 2.0
FLOW_VERY_LOW_LPM = 0.75

WATER_LEVEL_RISE_WARNING_CM = 1.0
WATER_LEVEL_RISE_CRITICAL_CM = 3.0

FLOW_DROP_WARNING_LPM = -0.5
FLOW_DROP_CRITICAL_LPM = -1.0


def classify_condition(features: DrainFeatures) -> str:
    """
    Determine the probable drainage condition using multiple sensor signals.

    Priority order:
        1. Severe blockage
        2. Partial blockage
        3. Heavy rainfall
        4. Abnormal flow
        5. Normal drainage
    """

    water = features.water_level_cm
    flow = features.flow_rate_lpm
    rainfall = features.rainfall

    water_rising = features.water_level_rising
    flow_decreasing = features.flow_rate_decreasing

    water_change = features.water_level_change
    flow_change = features.flow_rate_change

    # -----------------------------------------------------------------------
    # 1. SEVERE BLOCKAGE
    # -----------------------------------------------------------------------
    #
    # Strong combination:
    #   - very high water
    #   - very low flow
    #   - low/moderate rainfall
    #
    # OR:
    #   - high water
    #   - rapidly rising water
    #   - very low/decreasing flow
    # -----------------------------------------------------------------------

    severe_blockage = (
        (
            water >= WATER_LEVEL_CRITICAL_CM
            and flow <= FLOW_VERY_LOW_LPM
            and rainfall < 10
        )
        or
        (
            water >= WATER_LEVEL_HIGH_CM
            and water_change >= WATER_LEVEL_RISE_CRITICAL_CM
            and flow <= FLOW_LOW_LPM
            and flow_decreasing
            and rainfall < 10
        )
    )

    if severe_blockage:
        return "SEVERE_BLOCKAGE"

    # -----------------------------------------------------------------------
    # 2. PARTIAL BLOCKAGE
    # -----------------------------------------------------------------------
    #
    # Typical pattern:
    #
    #   Water ↑
    #   Flow ↓
    #   Rainfall low/moderate
    #
    # We require multiple indicators so high water alone does not become
    # a blockage.
    # -----------------------------------------------------------------------

    partial_blockage = (
        water >= WATER_LEVEL_WARNING_CM
        and flow <= FLOW_LOW_LPM
        and rainfall < 10
        and (
            water_rising
            or flow_decreasing
            or water_change >= WATER_LEVEL_RISE_WARNING_CM
            or flow_change <= FLOW_DROP_WARNING_LPM
        )
    )

    if partial_blockage:
        return "PARTIAL_BLOCKAGE"

    # -----------------------------------------------------------------------
    # 3. HEAVY RAINFALL
    # -----------------------------------------------------------------------
    #
    # Heavy rainfall should NOT be mistaken for blockage.
    #
    # Expected pattern:
    #
    #   Rainfall ↑
    #   Water ↑
    #   Flow remains healthy/increases
    # -----------------------------------------------------------------------

    heavy_rainfall = (
        rainfall >= 10
        and water >= WATER_LEVEL_WARNING_CM
        and flow > FLOW_LOW_LPM
        and not (
            flow_decreasing
            and flow <= FLOW_LOW_LPM
        )
    )

    if heavy_rainfall:
        return "HEAVY_RAINFALL"

    # -----------------------------------------------------------------------
    # 4. ABNORMAL FLOW
    # -----------------------------------------------------------------------
    #
    # Detect flow behaviour that does not reasonably match the other
    # measurements.
    # -----------------------------------------------------------------------

    abnormal_flow = (
        flow <= FLOW_VERY_LOW_LPM
        and water < WATER_LEVEL_WARNING_CM
        and rainfall < 5
    )

    if abnormal_flow:
        return "ABNORMAL_FLOW"

    # -----------------------------------------------------------------------
    # 5. NORMAL DRAINAGE
    # -----------------------------------------------------------------------

    return "NORMAL_DRAINAGE"