import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, forkJoin, map } from 'rxjs';

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

    created_at?: string;

  };

}


interface AnalysisResponse {

  success: boolean;

  drain_id: string;

  analysis: any;

}


@Injectable({
  providedIn: 'root'
})
export class DrainService {

  private readonly http =
    inject(HttpClient);


  private readonly apiUrl =
    'http://localhost:8000/api/v1';


  // ==========================================================
  // DASHBOARD
  // ==========================================================

  getDashboardData(
    drainId: string
  ): Observable<DrainDashboard> {

    return forkJoin({

      latest:
        this.http.get<LatestReadingResponse>(
          `${this.apiUrl}/drains/${drainId}/latest`
        ),

      analysis:
        this.http.get<AnalysisResponse>(
          `${this.apiUrl}/drains/${drainId}/analysis`
        )

    }).pipe(

      map(({ latest, analysis }) => {

        console.log(
          'LATEST API:',
          latest
        );

        console.log(
          'ANALYSIS API:',
          analysis
        );


        return {

          drain_id:
            latest.drain_id,

          latest_reading:
            latest.latest_reading,

          analysis:
            analysis.analysis

        } as DrainDashboard;

      })

    );

  }


  // ==========================================================
  // LATEST
  // ==========================================================

  getLatestReading(
    drainId: string
  ): Observable<LatestReadingResponse> {

    return this.http.get<LatestReadingResponse>(
      `${this.apiUrl}/drains/${drainId}/latest`
    );

  }


  // ==========================================================
  // ANALYSIS
  // ==========================================================

  getAnalysis(
    drainId: string
  ): Observable<AnalysisResponse> {

    return this.http.get<AnalysisResponse>(
      `${this.apiUrl}/drains/${drainId}/analysis`
    );

  }


  // ==========================================================
  // HISTORY
  // ==========================================================

  getHistory(
    drainId: string
  ): Observable<any> {

    return this.http.get<any>(
      `${this.apiUrl}/drains/${drainId}/history`
    );

  }

}