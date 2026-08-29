import { Component, OnInit, inject } from '@angular/core';
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
          this.dashboardData = data;
          this.loading = false;
        },

        error: () => {
          this.error = true;
          this.loading = false;
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