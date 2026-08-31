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
  timer,
  switchMap,
  catchError,
  of
} from 'rxjs';

import { DrainService } from '../core/services/drain.service';
import { DrainDashboard } from '../models/drain-dashboard.model';

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

  private refreshSubscription?: Subscription;

  private historySubscription?: Subscription;

  dashboardData: DrainDashboard | null = null;

  history: any[] = [];

  loading = true;

  error = false;

  readonly drainId = 'D001';


  // ==========================================================
  // INITIALIZE
  // ==========================================================

  ngOnInit(): void {

    this.loadDashboard();

    this.loadHistory();

    this.startLiveMonitoring();

  }


  // ==========================================================
  // MANUAL REFRESH
  // ==========================================================

  loadDashboard(): void {

    this.error = false;

    this.drainService
      .getDashboardData(this.drainId)
      .subscribe({

        next: (data) => {

          console.log(
            'DASHBOARD DATA:',
            data
          );

          this.dashboardData = data;

          this.loading = false;

          this.error = false;

          this.cdr.detectChanges();

        },

        error: (err) => {

          console.error(
            'DASHBOARD ERROR:',
            err
          );

          this.error = true;

          this.loading = false;

          this.cdr.detectChanges();

        }

      });

  }


  // ==========================================================
  // HISTORY
  // ==========================================================

  loadHistory(): void {

    this.historySubscription =
      this.drainService
        .getHistory(this.drainId)
        .subscribe({

          next: (response: any) => {

            console.log(
              'HISTORY DATA:',
              response
            );

            this.history =
              response?.readings ?? [];

            this.cdr.detectChanges();

          },

          error: (err) => {

            console.error(
              'HISTORY ERROR:',
              err
            );

            this.history = [];

          }

        });

  }


  // ==========================================================
  // LIVE MONITORING
  // ==========================================================

  startLiveMonitoring(): void {

    this.refreshSubscription =
      timer(3000, 3000)
        .pipe(

          switchMap(() =>
            this.drainService
              .getDashboardData(this.drainId)
          ),

          catchError((err) => {

            console.error(
              'LIVE REFRESH ERROR:',
              err
            );

            this.error = true;

            return of(null);

          })

        )
        .subscribe((data) => {

          if (!data) {
            return;
          }

          console.log(
            'LIVE UPDATE:',
            data
          );

          this.dashboardData = data;

          this.loading = false;

          this.error = false;

          this.cdr.detectChanges();

        });

  }


  // ==========================================================
  // CLEANUP
  // ==========================================================

  ngOnDestroy(): void {

    this.refreshSubscription?.unsubscribe();

    this.historySubscription?.unsubscribe();

  }


  // ==========================================================
  // CONDITION CSS CLASS
  // ==========================================================

  get conditionClass(): string {

    return (
      this.dashboardData
        ?.analysis
        ?.condition
        ?.toString()
        ?.toLowerCase() ?? ''
    );

  }


  // ==========================================================
  // SEVERITY CSS CLASS
  // ==========================================================

  get severityClass(): string {

    return (
      this.dashboardData
        ?.analysis
        ?.severity
        ?.toString()
        ?.toLowerCase() ?? ''
    );

  }


  // ==========================================================
  // LAST UPDATED
  // ==========================================================

  get lastUpdated(): string {

    const reading: any =
      this.dashboardData?.latest_reading;

    return (
      reading?.created_at ??
      reading?.timestamp ??
      ''
    );

  }


  // ==========================================================
  // TREND DATA
  // ==========================================================

  get trendData(): any[] {

    if (!this.history?.length) {

      return [];

    }

    return this.history.slice(-10);

  }


  // ==========================================================
  // TREND HEIGHT
  // ==========================================================

  getTrendHeight(value: number): number {

    const values =
      this.trendData
        .map(item =>
          Number(item.water_level_cm)
        )
        .filter(v => !isNaN(v));


    if (!values.length) {

      return 20;

    }


    const max =
      Math.max(...values);

    const min =
      Math.min(...values);


    if (max === min) {

      return 50;

    }


    return (
      15 +
      (
        (value - min) /
        (max - min)
      ) * 70
    );

  }

}