# FlowSentra API Contract

## 1. Purpose

This document defines the communication contract between the FlowSentra hardware, backend, intelligence layer, and frontend.

All modules must follow the field names and data formats defined here to avoid integration problems.

---

## 2. System Communication

Arduino UNO R4 WiFi
        ↓
Sensor Data
        ↓
FastAPI Backend
        ↓
Data Validation
        ↓
Database
        ↓
Intelligence Layer
        ↓
Drain Analysis
        ↓
Angular Dashboard

---

## 3. Sensor Reading API

### Endpoint

POST /api/v1/sensors/readings

### Purpose

Receives real-time sensor readings from the Arduino UNO R4 WiFi.

### Request Body

{
  "drain_id": "D001",
  "water_level_cm": 18.4,
  "flow_rate_lpm": 2.7,
  "rainfall": 0,
  "timestamp": "2026-08-29T10:30:00Z"
}

---

## 4. Sensor Data Fields

| Field | Type | Required | Description |
|---|---|---|---|
| drain_id | string | Yes | Unique ID of the monitored drain |
| water_level_cm | float | Yes | Water level in centimetres |
| flow_rate_lpm | float | Yes | Flow rate in litres per minute |
| rainfall | float | Yes | Rainfall measurement |
| timestamp | string | Yes | ISO 8601 timestamp |

---

## 5. Sensor Data Rules

### drain_id

Every monitoring node must have a unique drain ID.

Examples:

D001
D002
D003

### water_level_cm

Unit: centimetres (cm)

Example:

water_level_cm: 18.4

### flow_rate_lpm

Unit: litres per minute (L/min)

Example:

flow_rate_lpm: 2.7

### rainfall

The rainfall value depends on the selected rainfall sensor and its calibration.

The hardware module must document the calibration used.

### timestamp

Use ISO 8601 format.

Example:

2026-08-29T10:30:00Z

---

## 6. Sensor Reading Response

Successful submission:

{
  "success": true,
  "message": "Sensor reading received",
  "drain_id": "D001"
}

---

## 7. Drain Analysis

The intelligence layer converts sensor readings into a higher-level drainage assessment.

### Analysis Object

{
  "drain_id": "D001",
  "health_score": 72,
  "condition": "WARNING",
  "probable_cause": "PARTIAL_BLOCKAGE",
  "severity": "MEDIUM",
  "overflow_risk": 34,
  "sensor_confidence": 91,
  "maintenance_priority": "P2"
  "recommended_action": "Inspect the drain for possible restricted flow."
}

---

## 8. Analysis Fields

| Field | Type | Description |
|---|---|---|
| drain_id | string | Unique drain identifier |
| health_score | integer | Overall drainage health score |
| condition | string | Current drainage condition |
| probable_cause | string | Most likely cause |
| severity | string | Severity of the condition |
| overflow_risk | integer | Estimated overflow risk |
| sensor_confidence | integer | Confidence in sensor readings |
| maintenance_priority | string | Recommended maintenance priority |
| recommended_action | string | Recommended action based on the current drainage assessment

---

## 9. Health Score

The health score is represented from 0 to 100.

Higher score means better drainage condition.

Lower score means poorer drainage condition.

Initial interpretation:

| Score | Condition |
|---|---|
| 70–100 | Healthy / Normal |
| 40–69 | Warning |
| 0–39 | Critical |

The exact scoring algorithm will be finalized by the intelligence module.

---

## 10. Condition Values

Allowed values:

NORMAL
WARNING
CRITICAL

---

## 11. Severity Values

Allowed values:

LOW
MEDIUM
HIGH
CRITICAL

---

## 12. Probable Cause Values

Initial categories:

NORMAL_DRAINAGE
HEAVY_RAINFALL
PARTIAL_BLOCKAGE
SEVERE_BLOCKAGE
ABNORMAL_FLOW

Additional categories may be added if required by the intelligence module.

---

## 13. Overflow Risk

Overflow risk is represented from 0 to 100.

0 means very low risk.

100 means very high risk.

Example:

overflow_risk: 78

This indicates a high estimated overflow risk.

The exact calculation will be implemented by the intelligence module.

---

## 14. Sensor Confidence

Sensor confidence is represented from 0 to 100.

0 means very low confidence.

100 means very high confidence.

The value should represent the consistency and plausibility of the available sensor measurements.

Example:

sensor_confidence: 91

---

## 15. Maintenance Priority

Allowed values:

P1
P2
P3

| Priority | Meaning |
|---|---|
| P1 | Immediate attention |
| P2 | High priority |
| P3 | Routine inspection |

---

## 16. Dashboard APIs

### Get Latest Reading

GET /api/v1/drains/{drain_id}/latest

Example:

GET /api/v1/drains/D001/latest

---

### Get Drain Analysis

GET /api/v1/drains/{drain_id}/analysis

Example:

GET /api/v1/drains/D001/analysis

---

### Get Historical Readings

GET /api/v1/drains/{drain_id}/history

Example:

GET /api/v1/drains/D001/history

---

## 17. Example Dashboard Response

{
  "drain_id": "D001",
  "latest_reading": {
    "water_level_cm": 18.4,
    "flow_rate_lpm": 2.7,
    "rainfall": 0,
    "timestamp": "2026-08-29T10:30:00Z"
  },
  "analysis": {
    "health_score": 72,
    "condition": "WARNING",
    "probable_cause": "PARTIAL_BLOCKAGE",
    "severity": "MEDIUM",
    "overflow_risk": 34,
    "sensor_confidence": 91,
    "maintenance_priority": "P2"
    "recommended_action": "Inspect the drain for possible restricted flow."
  }
}

---

## 18. Error Response

All API errors should follow a consistent format.

Example:

{
  "success": false,
  "error": {
    "code": "INVALID_SENSOR_DATA",
    "message": "water_level_cm must be a numeric value"
  }
}

---

## 19. HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Invalid request |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Internal server error |

---

## 20. Integration Contract

### Hardware Team

The hardware module must provide:

- drain_id
- water_level_cm
- flow_rate_lpm
- rainfall
- timestamp

### Backend Team

The backend must:

- Accept sensor readings
- Validate incoming data
- Store readings
- Provide APIs
- Provide analysis results to the frontend

### Intelligence Team

The intelligence module consumes:

- water_level_cm
- flow_rate_lpm
- rainfall

The intelligence module produces:

- health_score
- condition
- probable_cause
- severity
- overflow_risk
- sensor_confidence
- maintenance_priority
- recommended_action

### Frontend Team

The frontend consumes backend APIs and displays:

- Current sensor values
- Drain condition
- Health score
- Probable cause
- Severity
- Overflow risk
- Sensor confidence
- Maintenance priority
- Alerts
- Recommendations

---

## 21. API Versioning

Current API version:

v1

All endpoints must use:

/api/v1/

Any breaking change to the API must be discussed with the team before implementation.

---

## 22. Single Source of Truth

This document is the common reference for communication between FlowSentra modules.

Team members should not independently rename or modify API fields.

If a change is required, update this document first and then update the affected modules.