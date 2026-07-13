import { Component, OnInit, inject, ChangeDetectorRef, ViewChildren, QueryList } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ButtonDef } from '../../models/screen.model';
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
  validationError: string | null = null;
  completed = false;
  serviceId: string | null = null;

  @ViewChildren(DynamicFieldComponent) dynamicFields!: QueryList<DynamicFieldComponent>;

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

  onAction(btn: ButtonDef) {
    if (btn.action === 'next_step' || btn.action === 'submit') {
      this.nextStep();
    } else {
      console.warn('Unhandled action:', btn.action);
    }
  }

  private nextStep() {
    let allValid = true;
    this.dynamicFields.forEach(field => {
      if (!field.validate()) {
        allValid = false;
      }
    });

    if (!allValid) {
      this.validationError = 'Please correct the errors before proceeding.';
      return;
    }

    this.validationError = null;
    const answers = this.stateService.getAllAnswers();
    const currentScreen = this.stateService.getScreen();

    if (!this.serviceId || !currentScreen) return;

    this.loading = true;
    this.apiService.nextStep(this.serviceId, currentScreen.id, answers).subscribe({
      next: (res) => {
        if (res.completed) {
          this.completed = true;
        } else if (res.next_screen) {
          this.stateService.setScreen(res.next_screen);
        }
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.error = 'Failed to load next screen: ' + (err.error?.detail || err.message);
        this.loading = false;
        console.error('Error loading next screen:', err);
        this.cdr.detectChanges();
      }
    });
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