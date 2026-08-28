# FlowSentra System Architecture

## 1. Overview

FlowSentra is a hardware-integrated IoT and intelligent drainage monitoring system designed to monitor urban drainage conditions in real time, identify abnormal drainage behaviour, estimate risk and severity, and support maintenance decisions.

The system follows:

Sense → Transmit → Validate → Analyse → Assess → Prioritize → Alert

## 2. High-Level Architecture

                    PHYSICAL DRAIN
                          |
                          v
                +------------------+
                |   SENSOR LAYER   |
                |                  |
                | • Water Level    |
                | • Flow Rate      |
                | • Rainfall       |
                +--------+---------+
                         |
                         v
              +---------------------+
              | Arduino UNO R4 WiFi |
              |                     |
              | • Read Sensors      |
              | • Validate Data     |
              | • Wi-Fi Transmission|
              +----------+----------+
                         |
                         | Wi-Fi
                         v
              +---------------------+
              |   FastAPI Backend   |
              |                     |
              | • Receive Data      |
              | • Validate Data     |
              | • Store Data        |
              | • Provide APIs      |
              +----------+----------+
                         |
                         v
              +---------------------+
              |  Intelligence Layer |
              |                     |
              | • Anomaly Detection |
              | • Cause Analysis    |
              | • Health Score      |
              | • Overflow Risk     |
              | • Sensor Confidence |
              | • Priority          |
              +----------+----------+
                         |
                         v
              +---------------------+
              |  Angular Dashboard  |
              |                     |
              | • Drain Status      |
              | • Sensor Values     |
              | • Health Score      |
              | • Risk              |
              | • Alerts            |
              | • Recommendations   |
              +---------------------+

## 3. System Layers

### 3.1 Physical Sensing Layer

The sensing layer collects information about the physical condition of the drainage system.

Primary parameters:

- Water Level
- Flow Rate
- Rainfall

Purpose:

These sensors provide the measurements required to determine whether the drainage system is behaving normally or showing abnormal patterns.

### 3.2 Edge Processing Layer

The Arduino UNO R4 WiFi acts as the edge controller.

Responsibilities:

- Read sensor measurements
- Perform basic validation
- Convert readings into usable units
- Assign the drain ID
- Generate timestamps
- Connect to Wi-Fi
- Transmit sensor readings to the backend

The Arduino focuses on reliable data acquisition and transmission. Higher-level analysis is handled by the backend and intelligence layer.

### 3.3 Backend Layer

The backend is implemented using Python and FastAPI.

Responsibilities:

- Receive sensor readings
- Validate incoming data
- Store sensor readings
- Provide APIs
- Provide historical sensor data
- Connect the intelligence layer with the application
- Serve data to the frontend

### 3.4 Intelligence Layer

The intelligence layer converts sensor measurements into meaningful drainage insights.

Responsibilities:

- Detect abnormal drainage behaviour
- Analyse relationships between sensor parameters
- Estimate drain health
- Identify probable causes
- Estimate overflow risk
- Estimate sensor confidence
- Determine severity
- Assign maintenance priority

The system should analyse multiple parameters instead of relying only on a single sensor threshold.

Example: Possible Blockage

Water Level ↑
Flow Rate ↓
Rainfall Moderate
        ↓
Possible Restricted Flow / Blockage

Example: Heavy Rainfall

Water Level ↑
Flow Rate ↑
Rainfall ↑↑
        ↓
Possible Heavy Rainfall Event

### 3.5 Visualization Layer

The frontend is implemented using Angular.

The dashboard displays:

- Drain status
- Water level
- Flow rate
- Rainfall
- Drain health score
- Probable cause
- Severity
- Overflow risk
- Sensor confidence
- Maintenance priority
- Alerts and recommendations

## 4. End-to-End Data Flow

Physical Sensors
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
Alert / Maintenance Recommendation

## 5. Core System Logic

FlowSentra follows:

Detection → Diagnosis → Validation → Risk Assessment → Prioritization → Action

### Detection

Identify whether the current drainage behaviour is normal or abnormal.

### Diagnosis

Analyse sensor measurements to determine the probable cause.

### Validation

Check the consistency and plausibility of available sensor measurements.

### Risk Assessment

Estimate the possibility of dangerous water-level or overflow conditions.

### Prioritization

Assign a maintenance priority based on severity and risk.

### Action

Generate an alert or recommended maintenance response.

## 6. Prototype Demonstration

The physical prototype will simulate different drainage conditions.

### Normal Condition

Normal Water Level
       +
Normal Flow
       +
Low/Normal Rainfall
       ↓
NORMAL

### Blockage Condition

Flow Restriction
       ↓
Flow Rate Decreases
       +
Water Level Increases
       ↓
ABNORMAL CONDITION
       ↓
Possible Blockage
       ↓
Health Score Decreases
       ↓
Risk Increases
       ↓
Maintenance Alert

### Heavy Rainfall Condition

Rainfall Increases
       ↓
Water Level Increases
       +
Flow Rate Also Increases
       ↓
Heavy Rainfall Condition

## 7. Module Responsibilities

| Module | Responsibility |
|---|---|
| Hardware | Sensor acquisition, Arduino firmware and physical prototype |
| Backend | APIs, data ingestion, database and server-side services |
| AI | Drain analysis, anomaly detection, risk and health assessment |
| Frontend | Dashboard, visualization and alerts |
| Data | Sample and development datasets |
| Docs | Architecture and technical documentation |

## 8. Hardware-to-Software Boundary

### Hardware

- Sensor acquisition
- Basic validation
- Data formatting
- Wi-Fi communication
- Physical prototype control

### Backend

- Data reception
- Data validation
- Data storage
- API services
- System integration

### Intelligence

- Anomaly detection
- Cause estimation
- Health assessment
- Risk assessment
- Maintenance prioritization

### Frontend

- Visualization
- Monitoring
- Alerts
- User interaction
- Maintenance insights

## 9. Scalability

The system uses a unique drain_id for each monitoring node.

This allows FlowSentra to scale from one prototype to multiple drainage monitoring nodes.

Drain D001 ─┐
Drain D002 ─┤
Drain D003 ─┤
Drain D004 ─┤
            ↓
     FlowSentra Backend
            ↓
     Intelligence Layer
            ↓
     Central Dashboard

## 10. Technology Stack

### Hardware

- Arduino UNO R4 WiFi
- Waterproof Ultrasonic Sensor
- Water Flow Sensor
- Rain Sensor
- Relay Module
- DC Water Pump
- LED
- Buzzer

### Backend

- Python
- FastAPI
- Firebase / Firestore

### Intelligence

- Python
- NumPy
- Pandas
- Scikit-learn

### Frontend

- Angular
- TypeScript
- HTML
- CSS

### Future Computer Vision

- OpenCV
- YOLO