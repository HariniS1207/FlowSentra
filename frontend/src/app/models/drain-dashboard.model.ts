import { SensorReading } from './sensor-reading.model';
import { DrainAnalysis } from './drain-analysis.model';

export interface DrainDashboard {
  drain_id: string;
  latest_reading: SensorReading;
  analysis: DrainAnalysis;
}