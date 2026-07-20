import { Component, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ButtonDef } from '../../models/screen.model';
import { CommonModule } from '@angular/common';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { LogicService } from '../../services/logic';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-player',
  imports: [CommonModule, DynamicFieldComponent],
  templateUrl: './player.html',
  styleUrl: './player.scss',
})
export class Player implements OnInit, OnDestroy {
  loading = true;
  error: string | null = null;
  validationError: string | null = null;
  private serviceId: string | null = null;

  private route = inject(ActivatedRoute);
  private apiService = inject(ApiService);
  public stateService = inject(StateService);
  private logicService = inject(LogicService);
  private cdr = inject(ChangeDetectorRef);
  private answerSubscription?: Subscription;

  ngOnInit() {
    this.answerSubscription = this.stateService.answerChanges$.subscribe(change => {
      const screen = this.stateService.getScreen();
      if (screen?.scripts) {
        const onChangeScripts = screen.scripts.filter(s => s.trigger === 'onChange' && s.targetComponentId === change.componentId);
        onChangeScripts.forEach(script => {
          this.logicService.execute(script.code, change);
        });
      }
    });

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

  ngOnDestroy() {
    if (this.answerSubscription) {
      this.answerSubscription.unsubscribe();
    }
  }

  private loadScreen(serviceId: string) {
    this.loading = true;
    this.error = null;
    this.apiService.start(serviceId).subscribe({
      next: (screen) => {
        this.stateService.setScreen(screen);
        if (screen.scripts) {
          const onLoadScripts = screen.scripts.filter(s => s.trigger === 'onLoad');
          onLoadScripts.forEach(script => {
            this.logicService.execute(script.code);
          });
        }
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

      if (!this.stateService.isFormValid()) {
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
          if (response && response.next_screen && response.next_screen.id) {
            this.stateService.setScreen(response.next_screen);
            if (response.next_screen.scripts) {
              const onLoadScripts = response.next_screen.scripts.filter((s: any) => s.trigger === 'onLoad');
              onLoadScripts.forEach((script: any) => {
                this.logicService.execute(script.code);
              });
            }
          }
          this.loading = false;
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.error = 'Failed to process next step: ' + err.message;
          this.loading = false;
          this.cdr.detectChanges();
        }
      });
    }
  }
}