export interface DrainAnalysis {
  drain_id: string;
  health_score: number;
  condition: 'NORMAL' | 'WARNING' | 'CRITICAL';
  probable_cause: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  overflow_risk: number;
  sensor_confidence: number;
  maintenance_priority: 'P1' | 'P2' | 'P3';
  recommended_action: string;
}