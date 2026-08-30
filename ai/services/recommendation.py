def generate_recommended_action(
    probable_cause: str,
    severity: str,
    overflow_risk: int,
    sensor_confidence: int,
) -> str:
    """
    Generate a human-readable action recommendation based on
    the combined intelligence result.
    """

    # ---------------------------------------------------------------
    # Sensor reliability issue
    # ---------------------------------------------------------------

    if sensor_confidence < 50:
        return (
            "Sensor readings appear unreliable. "
            "Inspect or recalibrate the sensors before making "
            "maintenance decisions."
        )

    # ---------------------------------------------------------------
    # Severe blockage
    # ---------------------------------------------------------------

    if probable_cause == "SEVERE_BLOCKAGE":
        if overflow_risk >= 80:
            return (
                "Immediate drain inspection and blockage removal "
                "recommended due to high overflow risk."
            )

        return (
            "Inspect the drain immediately for severe blockage "
            "and restricted flow."
        )

    # ---------------------------------------------------------------
    # Partial blockage
    # ---------------------------------------------------------------

    if probable_cause == "PARTIAL_BLOCKAGE":
        if overflow_risk >= 60:
            return (
                "High-priority inspection recommended. "
                "Clear possible blockage before water accumulation increases."
            )

        return (
            "Inspect the drain for possible restricted flow "
            "and early-stage blockage."
        )

    # ---------------------------------------------------------------
    # Heavy rainfall
    # ---------------------------------------------------------------

    if probable_cause == "HEAVY_RAINFALL":
        if overflow_risk >= 70:
            return (
                "Monitor the drain closely during heavy rainfall "
                "and prepare overflow mitigation if water continues rising."
            )

        return (
            "Continue monitoring the drain during the rainfall event "
            "and watch for increasing water levels."
        )

    # ---------------------------------------------------------------
    # Abnormal flow
    # ---------------------------------------------------------------

    if probable_cause == "ABNORMAL_FLOW":
        return (
            "Inspect the flow sensor and drainage path for abnormal "
            "flow behaviour."
        )

    # ---------------------------------------------------------------
    # Normal drainage
    # ---------------------------------------------------------------

    return (
        "Drainage conditions are normal. "
        "Continue routine monitoring."
    )