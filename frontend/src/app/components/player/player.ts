import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { ButtonDef } from '../../models/screen.model';

@Component({
  selector: 'app-player',
  imports: [CommonModule, DynamicFieldComponent],
  templateUrl: './player.html',
  styleUrl: './player.scss',
})
export class Player implements OnInit {
  loading = true;
  error: string | null = null;
  validationError: string | null = null;
  serviceId: string | null = null;

  private route = inject(ActivatedRoute);
  private apiService = inject(ApiService);
  public stateService = inject(StateService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const serviceId = params.get('service_id');
      this.serviceId = serviceId;
      if (serviceId) {
        this.loadScreen(serviceId);
      } else {
        this.error = 'No service ID provided';
        this.loading = false;
      }
    });
  }

  private loadScreen(serviceId: string) {
    this.loading = true;
    this.error = null;
    this.validationError = null;
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


  onButtonClick(btn: ButtonDef, currentScreenId: string) {
    if (btn.action === 'next_step' || btn.action === 'submit') {
      if (!this.serviceId) return;

      if (!this.stateService.validateScreen()) {
        this.validationError = 'Please fix the validation errors before proceeding.';
        return;
      }

      this.loading = true;
      this.validationError = null;

      const answers = this.stateService.getAllAnswers();
      this.apiService.nextStep(this.serviceId, currentScreenId, answers).subscribe({
        next: (screen) => {
          this.stateService.setScreen(screen);
          this.loading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = 'Failed to submit next step: ' + err.message;
          this.loading = false;
          console.error('Error submitting next step:', err);
          this.cdr.detectChanges();
        }
      });
    }
  }
}
