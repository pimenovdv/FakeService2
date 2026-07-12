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

  onAction(button: ButtonDef) {
    if (button.action === 'next_step' || button.action === 'submit') {
      const screen = this.stateService.getScreen();
      const serviceId = this.route.snapshot.paramMap.get('service_id');
      if (screen && serviceId) {
        this.loading = true;
        this.apiService.nextStep(serviceId, screen.id, this.stateService.getAllAnswers()).subscribe({
          next: (response) => {
            if (response && response.id) {
              this.stateService.setScreen(response);
            } else {
              // No more screens
              this.stateService.clearState();
              this.error = 'Flow completed successfully.';
            }
            this.loading = false;
            this.cdr.detectChanges();
          },
          error: (err) => {
            this.error = 'Failed to submit: ' + err.message;
            this.loading = false;
            console.error('Error submitting:', err);
            this.cdr.detectChanges();
          }
        });
      }
    }
  }

  private loadScreen(serviceId: string) {
    this.loading = true;
    this.error = null;
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
}
