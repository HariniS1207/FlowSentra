# FlowSentra

> Intelligent IoT-Based Drainage Monitoring and Risk Assessment System

FlowSentra is a hardware-integrated smart drainage monitoring system that combines real-time sensing, IoT connectivity, intelligent analysis, and a web-based dashboard to detect abnormal drainage conditions and support proactive maintenance.

The system monitors key drainage parameters such as water level, flow rate, and rainfall. Instead of simply displaying sensor values, FlowSentra analyses their relationships to identify possible drainage problems, estimate drain health and overflow risk, and generate maintenance priorities.

---

## Problem

Urban drainage systems are often inspected manually or reactively after problems such as water accumulation, blockage, or overflow become visible.

Traditional monitoring approaches have several limitations:

- Manual inspection is time-consuming.
- Drain conditions can change rapidly during rainfall.
- A single sensor threshold may not distinguish blockage from heavy rainfall.
- Maintenance teams may not know which drains require immediate attention.
- Existing monitoring systems may provide raw measurements without meaningful diagnosis or prioritization.

FlowSentra aims to provide continuous monitoring and actionable drainage intelligence.

---

## Proposed Solution

FlowSentra combines physical sensing with software intelligence to continuously monitor drainage conditions.

The system:

1. Collects drainage parameters using sensors.
2. Processes the readings using an Arduino UNO R4 WiFi.
3. Transmits the measurements through Wi-Fi.
4. Receives and validates the data through a FastAPI backend.
5. Stores the readings for monitoring and historical analysis.
6. Analyses multiple sensor parameters to identify abnormal behaviour.
7. Estimates probable causes such as partial blockage or heavy rainfall.
8. Calculates drain health and overflow risk.
9. Assigns maintenance priority.
10. Displays the results through an Angular dashboard.
11. Generates alerts and maintenance recommendations.

---

## Core Concept

Sense → Transmit → Validate → Analyse → Assess → Prioritize → Alert

---

## System Architecture

Physical Drain
      ↓
Sensors
      ↓
Arduino UNO R4 WiFi
      ↓
Wi-Fi
      ↓
FastAPI Backend
      ↓
Data Validation
      ↓
Database
      ↓
Intelligence Engine
      ↓
Drain Analysis
      ↓
Angular Dashboard
      ↓
Alerts / Maintenance Recommendations

Detailed architecture is available in:

docs/architecture/system-architecture.md

API communication specifications are available in:

docs/api/api-contract.md

---

## Hardware

### Main Components

- Arduino UNO R4 WiFi
- Waterproof Ultrasonic Sensor
- Water Flow Sensor
- Rain Sensor
- Relay Module
- DC Water Pump
- LED
- Buzzer
- Breadboard
- Jumper Wires
- Power Supply

The physical prototype simulates drainage conditions and demonstrates how sensor behaviour changes under normal flow, restricted flow, and rainfall conditions.

---

## Software Stack

### Frontend

- Angular
- TypeScript
- HTML
- CSS

### Backend

- Python
- FastAPI
- Firebase / Firestore

### Intelligence

- Python
- NumPy
- Pandas
- Scikit-learn

### Hardware

- Arduino UNO R4 WiFi
- Arduino IDE

---

## Key Features

### Real-Time Drain Monitoring

Continuously monitors physical drainage parameters through connected sensors.

### Multi-Parameter Analysis

Combines water level, flow rate, and rainfall rather than relying only on one threshold.

### Abnormal Condition Detection

Identifies deviations from expected drainage behaviour.

### Probable Cause Identification

Attempts to distinguish conditions such as:

- Normal drainage
- Heavy rainfall
- Partial blockage
- Severe blockage
- Abnormal flow

### Drain Health Score

Provides a 0–100 health score representing the estimated condition of the monitored drain.

### Overflow Risk

Estimates the current possibility of dangerous water-level or overflow conditions.

### Sensor Confidence

Indicates the reliability and consistency of the available sensor measurements.

### Maintenance Prioritization

Assigns maintenance priorities such as:

- P1 — Immediate attention
- P2 — High priority
- P3 — Routine inspection

### Alerts and Recommendations

Provides actionable information instead of displaying raw sensor readings alone.

---

## Example Detection Logic

### Normal Drainage

Normal Water Level
+
Normal Flow
+
Low/Normal Rainfall
↓
Normal Condition

### Possible Blockage

Water Level ↑
+
Flow Rate ↓
+
Rainfall Moderate
↓
Possible Restricted Flow
↓
Possible Blockage
↓
Health Score Decreases
↓
Risk Increases
↓
Maintenance Alert

### Heavy Rainfall

Rainfall ↑
+
Water Level ↑
+
Flow Rate ↑
↓
Possible Heavy Rainfall Event

This multi-parameter approach helps reduce the possibility of incorrectly identifying every rise in water level as a blockage.

---

## Project Modules

### Hardware Module

Responsible for:

- Sensor integration
- Arduino firmware
- Sensor readings
- Data validation
- Wi-Fi communication
- Physical prototype
- Local indicators and actuation

Location:

hardware/

### Backend Module

Responsible for:

- API development
- Sensor data ingestion
- Data validation
- Database communication
- Historical data
- Communication between system modules

Location:

backend/

### Intelligence Module

Responsible for:

- Anomaly detection
- Drain condition analysis
- Probable cause identification
- Health score
- Overflow risk
- Sensor confidence
- Maintenance priority

### Frontend Module

Responsible for:

- Dashboard
- Real-time monitoring
- Sensor visualization
- Drain health
- Risk indicators
- Alerts
- Recommendations

---

## Repository Structure

FlowSentra/
│
├── backend/
│   └── app/
│
├── hardware/
│   ├── circuits/
│   ├── firmware/
│   └── README.md
│
├── docs/
│   ├── architecture/
│   │   └── system-architecture.md
│   │
│   └── api/
│       └── api-contract.md
│
├── frontend/
│   └── src/
│
├── README.md
├── LICENSE
└── .gitignore

---

## Data Flow

Sensor readings are represented using the following core parameters:

- drain_id
- water_level_cm
- flow_rate_lpm
- rainfall
- timestamp

The backend processes these measurements and provides them to the intelligence layer.

The intelligence layer generates:

- health_score
- condition
- probable_cause
- severity
- overflow_risk
- sensor_confidence
- maintenance_priority

The frontend consumes this information and presents it through the dashboard.

---

## Prototype Demonstration

The prototype will demonstrate multiple controlled drainage scenarios.

### Scenario 1 — Normal Flow

Water flows normally through the prototype drainage channel.

Expected result:

Normal condition.

### Scenario 2 — Restricted Flow

The drainage path is partially restricted.

Expected sensor behaviour:

- Water level increases.
- Flow rate decreases.

Expected system result:

Possible partial blockage.

### Scenario 3 — Heavy Rainfall

Additional water is introduced to simulate heavy rainfall.

Expected sensor behaviour:

- Rainfall increases.
- Water level increases.
- Flow rate may also increase.

Expected system result:

Possible heavy rainfall condition.

The system should use the combined sensor behaviour to distinguish these scenarios.

---

## Scalability

Each monitoring node is assigned a unique drain_id.

Example:

D001
D002
D003
D004

This allows the prototype architecture to be extended from a single monitored drain to multiple distributed drainage monitoring nodes.

Multiple nodes can communicate with a central backend and dashboard.

---

## Development Principle

FlowSentra is designed as a modular system.

Hardware, backend, intelligence, and frontend components communicate through clearly defined interfaces.

The API contract is maintained in:

docs/api/api-contract.md

The system architecture is maintained in:

docs/architecture/system-architecture.md

Any breaking change to the communication interface should be discussed by the team before implementation.

---

## Project Status

Current development stages:

- [x] Repository setup
- [x] Project architecture defined
- [x] API contract defined
- [ ] Hardware integration
- [ ] Sensor testing
- [ ] Arduino firmware
- [ ] Backend API
- [ ] Database integration
- [ ] Intelligence engine
- [ ] Angular dashboard
- [ ] Hardware-software integration
- [ ] End-to-end testing
- [ ] Demo preparation

---

## Team

FlowSentra is developed as a four-member hackathon project.

### Team Roles

- Hardware & IoT
- Backend & Database
- Intelligence / AI
- Frontend & UI

Responsibilities may overlap during integration and final testing.

---

## Future Scope

Potential future improvements include:

- Multiple distributed drainage nodes
- Long-term drainage behaviour analysis
- Predictive blockage detection
- Computer vision for visual drain inspection
- GIS-based drain mapping
- Mobile notifications
- Automated maintenance scheduling
- Integration with municipal infrastructure
- Solar-powered monitoring nodes
- Edge AI for offline analysis

---

## License

This project is developed for hackathon and research purposes.

See the LICENSE file for details.