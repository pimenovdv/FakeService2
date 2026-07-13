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
  public serviceId: string | null = null;

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

  onButtonClick(btn: ButtonDef) {
    if (btn.action === 'next_step' || btn.action === 'submit') {
      this.stateService.setSubmitAttempted(true);

      if (!this.stateService.isFormValid() || !this.stateService.validateScreen()) {
        this.validationError = 'Please correct the errors before proceeding.';
        return;
      }

      this.validationError = null;
      this.loading = true;
      const currentScreen = this.stateService.getScreen();
      if (!currentScreen || !this.serviceId) {
         this.error = 'No active screen or service ID';
         this.loading = false;
         return;
      }

      const answers = this.stateService.getAllAnswers();

      this.apiService.nextStep(this.serviceId, currentScreen.id, answers).subscribe({
        next: (response) => {
          if (response && response.id) {
            this.stateService.setScreen(response);
          } else if (response && response.next_screen) {
            this.stateService.setScreen(response.next_screen);
          }
          this.loading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = 'Failed to process next step: ' + err.message;
          this.loading = false;
          console.error('Error processing next step:', err);
          this.cdr.detectChanges();
        }
      });
    }
  }
}
