from ai.models.schemas import DrainFeatures


def classify_severity(
    features: DrainFeatures,
    probable_cause: str,
    health_score: int,
    overflow_risk: int,
) -> str:
    """
    Determine drainage severity from the combined condition,
    health score and overflow risk.
    """

    # ---------------------------------------------------------------
    # CRITICAL
    # ---------------------------------------------------------------

    if (
        probable_cause == "SEVERE_BLOCKAGE"
        and (
            health_score <= 30
            or overflow_risk >= 75
        )
    ):
        return "CRITICAL"

    if overflow_risk >= 90:
        return "CRITICAL"

    # ---------------------------------------------------------------
    # HIGH
    # ---------------------------------------------------------------

    if probable_cause == "SEVERE_BLOCKAGE":
        return "HIGH"

    if (
        probable_cause == "PARTIAL_BLOCKAGE"
        and overflow_risk >= 60
    ):
        return "HIGH"

    if overflow_risk >= 70:
        return "HIGH"

    # ---------------------------------------------------------------
    # MEDIUM
    # ---------------------------------------------------------------

    if probable_cause == "PARTIAL_BLOCKAGE":
        return "MEDIUM"

    if probable_cause == "ABNORMAL_FLOW":
        return "MEDIUM"

    if overflow_risk >= 40:
        return "MEDIUM"

    # ---------------------------------------------------------------
    # LOW
    # ---------------------------------------------------------------

    return "LOW"