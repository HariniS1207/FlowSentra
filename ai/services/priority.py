from ai.models.schemas import DrainFeatures


def calculate_maintenance_priority(
    probable_cause: str,
    severity: str,
    health_score: int,
    overflow_risk: int,
    sensor_confidence: int,
) -> str:
    """
    Determine maintenance priority.

    P1 = Immediate attention
    P2 = High priority
    P3 = Routine inspection
    """

    # ---------------------------------------------------------------
    # P1 — Immediate attention
    # ---------------------------------------------------------------

    if severity == "CRITICAL":
        return "P1"

    if overflow_risk >= 80 and health_score <= 40:
        return "P1"

    if probable_cause == "SEVERE_BLOCKAGE" and overflow_risk >= 70:
        return "P1"

    # ---------------------------------------------------------------
    # P2 — High priority
    # ---------------------------------------------------------------

    if severity == "HIGH":
        return "P2"

    if probable_cause == "PARTIAL_BLOCKAGE":
        return "P2"

    if overflow_risk >= 50:
        return "P2"

    if health_score < 60:
        return "P2"

    # ---------------------------------------------------------------
    # P3 — Routine inspection
    # ---------------------------------------------------------------

    return "P3"