import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-player',
  imports: [CommonModule, DynamicFieldComponent],
  templateUrl: './player.html',
  styleUrl: './player.scss',
})
export class Player implements OnInit {
  loading = true;
  error: string | null = null;
  submitError: string | null = null;
  serviceId: string | null = null;
  isFinished = false;

  private route = inject(ActivatedRoute);
  private apiService = inject(ApiService);
  public stateService = inject(StateService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      this.serviceId = params.get('service_id');
      if (this.serviceId) {
        this.loadScreen(this.serviceId);
      } else {
        this.error = 'No service ID provided';
        this.loading = false;
      }
    });
  }

  private loadScreen(serviceId: string) {
    this.loading = true;
    this.error = null;
    this.submitError = null;
    this.isFinished = false;
    this.apiService.start(serviceId).subscribe({
      next: (screen) => {
        this.stateService.setScreen(screen);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Failed to load screen: ' + err.message;
        this.loading = false;
        console.error('Error loading screen:', err);
        this.cdr.detectChanges();
      }
    });
  }

  onButtonClick(action: string) {
    if (action === 'next_step' || action === 'submit') {
      if (!this.stateService.isScreenValid()) {
        return;
      }
      this.loading = true;
      this.submitError = null;
      const currentScreen = this.stateService.getScreen();
      if (!currentScreen || !this.serviceId) return;

      const answers = this.stateService.getAllAnswers();
      this.apiService.nextStep(this.serviceId, currentScreen.id, answers).subscribe({
        next: (response) => {
          this.loading = false;
          if (response.id) {
            // It's a new screen
            this.stateService.setScreen(response);
          } else {
            // It's likely a completion payload, e.g. { message: "Success" }
            this.isFinished = true;
            this.stateService.clearState();
          }
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.submitError = 'Failed to submit: ' + err.message;
          this.loading = false;
          console.error('Error submitting screen:', err);
          this.cdr.detectChanges();
        }
      });
    } else if (action === 'cancel') {
      // Handle cancel if needed
      this.error = 'Process cancelled.';
      this.stateService.clearState();
    }
  }
}
