import {
  Component,
  OnInit,
  OnDestroy,
  ChangeDetectorRef,
  inject
} from '@angular/core';

import { CommonModule } from '@angular/common';

import {
  Subscription,
  interval,
  startWith,
  switchMap,
  forkJoin
} from 'rxjs';

import { DrainService } from '../core/services/drain.service';
import { DrainDashboard } from '../models/drain-dashboard.model';

interface SensorReading {
  drain_id: string;
  water_level_cm: number;
  flow_rate_lpm: number;
  rainfall: number;
  timestamp: string;
  created_at?: string;
}

interface HistoryResponse {
  success: boolean;
  drain_id: string;
  readings: SensorReading[];
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit, OnDestroy {

  private readonly drainService = inject(DrainService);
  private readonly cdr = inject(ChangeDetectorRef);

  private dashboardSubscription?: Subscription;

  dashboardData: DrainDashboard | null = null;

  loading = true;
  error = false;

  readonly drainId = 'D001';

  // ---------------------------------------------------------
  // GRAPH DATA
  // ---------------------------------------------------------

  historyReadings: SensorReading[] = [];

  readonly chartWidth = 1000;
  readonly chartHeight = 260;
  readonly chartPadding = 25;

  chartPoints = '';

  minWaterLevel = 0;
  maxWaterLevel = 0;

  // ---------------------------------------------------------
  // LIFECYCLE
  // ---------------------------------------------------------

  ngOnInit(): void {
    this.startLiveMonitoring();
  }

  ngOnDestroy(): void {
    this.dashboardSubscription?.unsubscribe();
  }

  // ---------------------------------------------------------
  // MANUAL REFRESH
  // ---------------------------------------------------------

  loadDashboard(): void {
    this.loading = true;
    this.error = false;

    this.loadDashboardData();
  }

  // ---------------------------------------------------------
  // LOAD DASHBOARD + HISTORY
  // ---------------------------------------------------------

  private loadDashboardData(): void {

    forkJoin({
      dashboard: this.drainService.getDashboardData(this.drainId),
      history: this.drainService.getHistory(this.drainId)
    }).subscribe({

      next: (result) => {

        console.log(
          'DASHBOARD RECEIVED DATA:',
          result.dashboard
        );

        console.log(
          'HISTORY RECEIVED DATA:',
          result.history
        );

        this.dashboardData = result.dashboard;

        const historyResponse =
          result.history as HistoryResponse;

        this.historyReadings =
          historyResponse.readings ?? [];

        this.historyReadings.sort(
          (a, b) =>
            new Date(a.timestamp).getTime() -
            new Date(b.timestamp).getTime()
        );

        this.buildChart();

        this.loading = false;
        this.error = false;

        this.cdr.detectChanges();

        console.log(
          'History count:',
          this.historyReadings.length
        );

        console.log(
          'Chart points:',
          this.chartPoints
        );
      },

      error: (err) => {

        console.error(
          'DASHBOARD / HISTORY API ERROR:',
          err
        );

        this.error = true;
        this.loading = false;

        this.cdr.detectChanges();
      }
    });
  }

  // ---------------------------------------------------------
  // LIVE MONITORING
  // ---------------------------------------------------------

  private startLiveMonitoring(): void {

    this.dashboardSubscription = interval(3000)
      .pipe(
        startWith(0),

        switchMap(() =>
          forkJoin({
            dashboard:
              this.drainService.getDashboardData(
                this.drainId
              ),

            history:
              this.drainService.getHistory(
                this.drainId
              )
          })
        )
      )
      .subscribe({

        next: (result) => {

          this.dashboardData =
            result.dashboard;

          const historyResponse =
            result.history as HistoryResponse;

          this.historyReadings =
            historyResponse.readings ?? [];

          this.historyReadings.sort(
            (a, b) =>
              new Date(a.timestamp).getTime() -
              new Date(b.timestamp).getTime()
          );

          this.buildChart();

          this.loading = false;
          this.error = false;

          this.cdr.detectChanges();

          console.log(
            'LIVE DASHBOARD UPDATED'
          );

          console.log(
            'Latest:',
            result.dashboard.latest_reading
          );

          console.log(
            'History count:',
            this.historyReadings.length
          );

          console.log(
            'Chart points:',
            this.chartPoints
          );
        },

        error: (err) => {

          console.error(
            'LIVE DASHBOARD ERROR:',
            err
          );

          this.error = true;
          this.loading = false;

          this.cdr.detectChanges();
        }
      });
  }

  // ---------------------------------------------------------
  // BUILD WATER LEVEL GRAPH
  // ---------------------------------------------------------

  private buildChart(): void {

    if (this.historyReadings.length === 0) {

      this.chartPoints = '';
      this.minWaterLevel = 0;
      this.maxWaterLevel = 0;

      return;
    }

    const values =
      this.historyReadings.map(
        reading => reading.water_level_cm
      );

    this.minWaterLevel =
      Math.min(...values);

    this.maxWaterLevel =
      Math.max(...values);

    let range =
      this.maxWaterLevel -
      this.minWaterLevel;

    if (range === 0) {
      range = 1;
    }

    const usableWidth =
      this.chartWidth -
      this.chartPadding * 2;

    const usableHeight =
      this.chartHeight -
      this.chartPadding * 2;

    const count =
      this.historyReadings.length;

    const points: string[] = [];

    this.historyReadings.forEach(
      (reading, index) => {

        const x =
          count === 1
            ? this.chartWidth / 2
            : this.chartPadding +
              (
                index /
                (count - 1)
              ) *
              usableWidth;

        const y =
          this.chartHeight -
          this.chartPadding -
          (
            (
              reading.water_level_cm -
              this.minWaterLevel
            ) / range
          ) *
          usableHeight;

        points.push(
          `${x.toFixed(2)},${y.toFixed(2)}`
        );
      }
    );

    this.chartPoints =
      points.join(' ');
  }

  // ---------------------------------------------------------
  // GRAPH HELPERS
  // ---------------------------------------------------------

  get chartLatestValue(): number {

    if (!this.historyReadings.length) {
      return 0;
    }

    return this.historyReadings[
      this.historyReadings.length - 1
    ].water_level_cm;
  }

  // ---------------------------------------------------------
  // CSS CLASSES
  // ---------------------------------------------------------
  get conditionDescription(): string {

  const cause = this.dashboardData?.analysis.probable_cause
    ?.toString()
    .trim()
    .toUpperCase();

  switch (cause) {

    case 'NORMAL_DRAINAGE':
      return 'Water level and flow remain within normal operating patterns.';

    case 'PARTIAL_BLOCKAGE':
      return 'Water level is rising while flow is low, indicating a possible partial restriction.';

    case 'SEVERE_BLOCKAGE':
      return 'Water level is critically high while flow remains very low, indicating a probable severe restriction.';

    case 'HEAVY_RAINFALL':
      return 'Increased water level and flow are consistent with rainfall-driven drainage load.';

    case 'ABNORMAL_FLOW':
      return 'Flow behaviour differs from the expected drainage pattern and requires inspection.';

    default:
      return 'Sensor conditions are being evaluated for possible drainage abnormalities.';
  }
}
  get conditionClass(): string {

    return this.dashboardData?.analysis.condition
      ?.toLowerCase() ?? '';
  }

  get severityClass(): string {

    return this.dashboardData?.analysis.severity
      ?.toLowerCase() ?? '';
  }
  get rainStatus(): string {
  const value = this.dashboardData?.latest_reading.rainfall;

  if (value === undefined || value === null) {
    return 'UNKNOWN';
  }

  if (value >= 900) {
    return 'NO RAIN';
  }

  if (value >= 600) {
    return 'LIGHT RAIN';
  }

  if (value >= 350) {
    return 'MODERATE RAIN';
  }

  return 'HEAVY RAIN';
}

get rainStatusClass(): string {
  return this.rainStatus
    .toLowerCase()
    .replace(' ', '-');
}
}