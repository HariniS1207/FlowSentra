import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

import { DrainDashboard } from '../../models/drain-dashboard.model';

interface LatestReadingResponse {
  success: boolean;
  drain_id: string;
  latest_reading: {
    drain_id: string;
    water_level_cm: number;
    flow_rate_lpm: number;
    rainfall: number;
    timestamp: string;
  };
}

@Injectable({
  providedIn: 'root'
})
export class DrainService {

  private readonly http = inject(HttpClient);

  private readonly apiUrl = 'http://localhost:8000/api/v1';

  getDashboardData(drainId: string): Observable<DrainDashboard> {

    return this.http
      .get<LatestReadingResponse>(
        `${this.apiUrl}/drains/${drainId}/latest`
      )
      .pipe(
        map(response => {

          console.log('FlowSentra API response:', response);

          return {
            drain_id: response.drain_id,

            latest_reading: response.latest_reading,

            /*
             * AI analysis will be connected later.
             * For now, keep the dashboard structure valid
             * without pretending these are real AI results.
             */
            analysis: {
              drain_id: response.drain_id,
              health_score: 0,
              condition: 'NORMAL',
              probable_cause: 'NORMAL_DRAINAGE',
              severity: 'LOW',
              overflow_risk: 0,
              sensor_confidence: 0,
              maintenance_priority: 'P3',
              recommended_action:
                'Awaiting intelligence analysis.'
            }
          };

        })
      );
  }


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