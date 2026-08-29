export interface SensorReading {
  drain_id: string;
  water_level_cm: number;
  flow_rate_lpm: number;
  rainfall: number;
  timestamp: string;
}