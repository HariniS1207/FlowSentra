import { Component, OnInit, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';

import { DrainService } from '../core/services/drain.service';
import { DrainDashboard } from '../models/drain-dashboard.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss'
})
export class Dashboard implements OnInit {

  private readonly drainService = inject(DrainService);
  private readonly cdr = inject(ChangeDetectorRef);
  dashboardData: DrainDashboard | null = null;
  loading = true;
  error = false;

  readonly drainId = 'D001';

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {

  this.loading = true;
  this.error = false;

  this.drainService
    .getDashboardData(this.drainId)
    .subscribe({
      next: (data) => {

          console.log('DASHBOARD RECEIVED DATA:', data);

          this.dashboardData = data;

          console.log('DASHBOARD DATA SET:', this.dashboardData);

          this.loading = false;

          this.cdr.detectChanges();

          console.log('LOADING STATE:', this.loading);
        },

      error: (err) => {

        console.error('DASHBOARD API ERROR:', err);

        this.error = true;
        this.loading = false;

        console.log('LOADING STATE AFTER ERROR:', this.loading);
      }
    });
}

  get conditionClass(): string {
    return this.dashboardData?.analysis.condition
      ?.toLowerCase() ?? '';
  }

  get severityClass(): string {
    return this.dashboardData?.analysis.severity
      ?.toLowerCase() ?? '';
  }
}