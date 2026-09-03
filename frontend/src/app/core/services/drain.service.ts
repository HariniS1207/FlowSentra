import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, map } from 'rxjs';

import { DrainDashboard } from '../../models/drain-dashboard.model';

interface LatestReading {
  drain_id: string;
  water_level_cm: number;
  flow_rate_lpm: number;
  rainfall: number;
  timestamp: string;
  created_at?: string;
}

interface LatestReadingResponse {
  success: boolean;
  drain_id: string;
  latest_reading: {
    drain_id: string;
    water_level_cm: number;
    flow_rate_lpm: number;
    rainfall: number;
    timestamp: string;
    created_at: string;
  };
}

interface Analysis {
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

interface AnalysisResponse {
  success: boolean;
  drain_id: string;
  analysis: Analysis;
  explanation: string;
}

interface HistoryResponse {
  success: boolean;
  drain_id: string;
  readings: LatestReading[];
}

@Injectable({
  providedIn: 'root'
})
export class DrainService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/v1';

  /**
   * Get all data required by the dashboard.
   *
   * Combines:
   *   1. Latest sensor reading
   *   2. AI drainage analysis
   *   3. Recent sensor history
   */
  getDashboardData(drainId: string): Observable<DrainDashboard> {

    const latest$ = this.http.get<LatestReadingResponse>(
      `${this.apiUrl}/drains/${drainId}/latest`
    );

    const analysis$ = this.http.get<AnalysisResponse>(
      `${this.apiUrl}/drains/${drainId}/analysis`
    );

    const history$ = this.http.get<HistoryResponse>(
      `${this.apiUrl}/drains/${drainId}/history`
    );

    return forkJoin({
      latest: latest$,
      analysis: analysis$,
      history: history$
    }).pipe(
      map(response => {

        console.log('FlowSentra latest response:', response.latest);
        console.log('FlowSentra AI response:', response.analysis);
        console.log('FlowSentra history response:', response.history);

        return {
          drain_id: response.latest.drain_id,

          latest_reading: response.latest.latest_reading,

          analysis: response.analysis.analysis,

          history: response.history.readings
        } as DrainDashboard;

      })
    );
  }

  /**
   * Get the latest sensor reading only.
   */
  getLatestReading(drainId: string): Observable<LatestReadingResponse> {

    return this.http.get<LatestReadingResponse>(
      `${this.apiUrl}/drains/${drainId}/latest`
    );
  }

  /**
   * Get the current AI drainage analysis.
   */
  getAnalysis(drainId: string): Observable<AnalysisResponse> {

    return this.http.get<AnalysisResponse>(
      `${this.apiUrl}/drains/${drainId}/analysis`
    );
  }

  /**
   * Get recent sensor history.
   */
  getHistory(drainId: string): Observable<HistoryResponse> {

    return this.http.get<HistoryResponse>(
      `${this.apiUrl}/drains/${drainId}/history`
    );
  }
}