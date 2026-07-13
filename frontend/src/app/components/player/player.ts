import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { ButtonDef, ComponentDef } from '../../models/screen.model';

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
  successMessage: string | null = null;

  private route = inject(ActivatedRoute);
  private apiService = inject(ApiService);
  public stateService = inject(StateService);
  private cdr = inject(ChangeDetectorRef);

  ngOnInit() {
    this.route.paramMap.subscribe(params => {
      const serviceId = params.get('service_id');
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
    this.successMessage = null;
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

  onActionClick(btn: ButtonDef, components: ComponentDef[]) {
    if (btn.action === 'next_step') {
      if (!this.stateService.isFormValid(components)) {
        this.validationError = 'Please fix validation errors before proceeding.';
        return;
      }
      this.validationError = null;

      const currentScreen = this.stateService.getScreen();
      if (!currentScreen) return;

      const serviceId = this.route.snapshot.paramMap.get('service_id');
      if (!serviceId) return;

      const answers = this.stateService.getAllAnswers();
      this.loading = true;

      this.apiService.nextStep(serviceId, currentScreen.id, answers).subscribe({
        next: (response) => {
          if (response && response.id) {
            // Looks like a next screen
            this.stateService.setScreen(response);
          } else {
            // Completion or other payload
            this.successMessage = 'Process completed successfully!'; // Or a better success state
            this.stateService.clearState();
          }
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
    } else if (btn.action === 'cancel') {
      this.error = 'Process cancelled.';
      this.stateService.clearState();
    } else if (btn.action === 'submit') {
       // Typically similar to next_step but maybe handles differently at the end
       this.onActionClick({ ...btn, action: 'next_step' }, components);
    }
  }
}
