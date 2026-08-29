import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';

import { DrainDashboard } from '../../models/drain-dashboard.model';

@Injectable({
  providedIn: 'root'
})
export class DrainService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getDashboardData(drainId: string): Observable<DrainDashboard> {

    /*
     * Temporary data provider.
     *
     * This has the SAME structure as the agreed
     * FlowSentra dashboard API response.
     *
     * When FastAPI is ready, this method will be
     * replaced with the real API request.
     */

    const dashboardData: DrainDashboard = {

      drain_id: drainId,

      latest_reading: {
        drain_id: drainId,
        water_level_cm: 18.4,
        flow_rate_lpm: 2.7,
        rainfall: 0,
        timestamp: new Date().toISOString()
      },

      analysis: {
        drain_id: drainId,
        health_score: 72,
        condition: 'WARNING',
        probable_cause: 'PARTIAL_BLOCKAGE',
        severity: 'MEDIUM',
        overflow_risk: 34,
        sensor_confidence: 91,
        maintenance_priority: 'P2',
        recommended_action:
          'Inspect the drain for possible restricted flow.'
      }

    };

    return of(dashboardData);
  }


  /*
   * Real FastAPI endpoints
   */

  getLatestReading(drainId: string): Observable<unknown> {

    return this.http.get(
      `${this.apiUrl}/drains/${drainId}/latest`
    );

  }


  getAnalysis(drainId: string): Observable<unknown> {

    return this.http.get(
      `${this.apiUrl}/drains/${drainId}/analysis`
    );

  }


  getHistory(drainId: string): Observable<unknown> {

    return this.http.get(
      `${this.apiUrl}/drains/${drainId}/history`
    );

  }

}