import { Component, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ButtonDef } from '../../models/screen.model';
import { CommonModule } from '@angular/common';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { LogicService } from '../../services/logic';
import { DraftService } from '../../services/draft';
import { Subscription } from 'rxjs';
import { jsPDF } from 'jspdf';
import html2canvas from 'html2canvas';

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
  private draftService = inject(DraftService);
  private cdr = inject(ChangeDetectorRef);
  private answerSubscription?: Subscription;

  ngOnInit() {
    this.answerSubscription = this.stateService.answerChanges$.subscribe(change => {
      const screen = this.stateService.getScreen();
      if (screen) {
        if (this.serviceId) {
          const autoSaveKey = `autosave_${this.serviceId}_${screen.id}`;
          localStorage.setItem(autoSaveKey, JSON.stringify(this.stateService.getAllAnswers()));
          this.draftService.saveDraft(this.serviceId, screen, this.stateService.getAllAnswers());
        }

        if (screen.scripts) {
          const onChangeScripts = screen.scripts.filter(s => s.trigger === 'onChange' && s.targetComponentId === change.componentId);
          onChangeScripts.forEach(script => {
            this.logicService.execute(script.code, change);
          });
        }
      }
    });

    this.route.paramMap.subscribe(params => {
      const serviceId = params.get('service_id');
      this.serviceId = serviceId;
      if (serviceId) {
        const isResume = this.route.snapshot.queryParamMap.get('resume') === 'true';
        if (isResume) {
           this.resumeDraft(serviceId);
        } else {
           this.loadScreen(serviceId);
        }
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

  private resumeDraft(serviceId: string) {
     this.loading = true;
     this.error = null;
     const draft = this.draftService.getDraft(serviceId);

     if (draft) {
       this.stateService.setScreen(draft.screen);
       this.stateService.restoreAnswers(draft.answers);

       if (draft.screen.scripts) {
          const onLoadScripts = draft.screen.scripts.filter(s => s.trigger === 'onLoad');
          onLoadScripts.forEach(script => {
            this.logicService.execute(script.code);
          });
       }

       this.loading = false;
       this.cdr.detectChanges();
     } else {
       // Draft not found, fallback to loading the initial screen
       this.loadScreen(serviceId);
     }
  }

  private loadScreen(serviceId: string) {
    this.loading = true;
    this.error = null;
    this.apiService.start(serviceId).subscribe({
      next: (screen) => {
        this.stateService.setScreen(screen);
        this.draftService.saveDraft(serviceId, screen, {});

        const autoSaveKey = `autosave_${serviceId}_${screen.id}`;
        const savedAnswersStr = localStorage.getItem(autoSaveKey);
        if (savedAnswersStr) {
          try {
            const savedAnswers = JSON.parse(savedAnswersStr);
            this.stateService.restoreAnswers(savedAnswers);
            this.draftService.saveDraft(serviceId, screen, savedAnswers);
          } catch (e) {
            console.error('Failed to parse autosave data', e);
          }
        }

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
  getThemeStyles(theme?: any) {
    if (!theme) return {};
    return {
      'background-color': theme.backgroundColor || '',
      'color': theme.textColor || '',
      'font-family': theme.fontFamily || '',
      '--theme-primary': theme.primaryColor || ''
    };
  }

  async exportPdf() {
    this.loading = true;
    this.cdr.detectChanges();
    try {
      const element = document.querySelector('.screen-layout') as HTMLElement;
      if (!element) {
        throw new Error('Screen layout element not found');
      }

      // Hide action buttons during PDF generation
      const buttonsContainer = element.querySelector('.flex.justify-end.gap-2.mt-4') as HTMLElement;
      if (buttonsContainer) {
        buttonsContainer.style.display = 'none';
      }

      const canvas = await html2canvas(element, { scale: 2 });

      if (buttonsContainer) {
        buttonsContainer.style.display = ''; // Restore buttons
      }

      const imgData = canvas.toDataURL('image/jpeg', 0.95);
      const pdf = new jsPDF({
        orientation: 'p',
        unit: 'mm',
        format: 'a4'
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width;

      pdf.addImage(imgData, 'JPEG', 0, 0, pdfWidth, pdfHeight);

      const screen = this.stateService.getScreen();
      const filename = screen ? `screen_${screen.id}.pdf` : 'screen_export.pdf';
      pdf.save(filename);
    } catch (err: any) {
      this.error = 'Failed to export PDF: ' + err.message;
      console.error('PDF Export error:', err);
    } finally {
      this.loading = false;
      this.cdr.detectChanges();
    }
  }

  onButtonClick(btn: ButtonDef) {
    if (btn.confirmMessage && !window.confirm(btn.confirmMessage)) {
      return;
    }

    if (btn.action === 'export_pdf') {
      this.exportPdf();
      return;
    }

    if (btn.action === 'next_step' || btn.action === 'submit') {
      this.stateService.setSubmitAttempted(true);

      let hasErrors = false;
      this.validationError = null;

      if (!this.stateService.isFormValid()) {
        this.validationError = 'Please correct the errors before proceeding.';
        hasErrors = true;
      }

      const currentScreen = this.stateService.getScreen();
      if (currentScreen?.crossValidations) {
        const crossErrors = this.stateService.evaluateCrossValidations(currentScreen.crossValidations);
        if (crossErrors.length > 0) {
          const crossErrorStr = crossErrors.join('. ');
          if (this.validationError) {
             this.validationError += ' ' + crossErrorStr;
          } else {
             this.validationError = crossErrorStr;
          }
          hasErrors = true;
        }
      }

      if (hasErrors) {
        return;
      }

      this.loading = true;
      if (!currentScreen || !this.serviceId) {
         this.error = 'No active screen or service ID';
         this.loading = false;
         return;
      }

      const answers = this.stateService.getAllAnswers();

      this.apiService.nextStep(this.serviceId, currentScreen.id, answers).subscribe({
        next: (response) => {
          // Clear autosave for the current screen since it was successfully submitted
          if (this.serviceId && currentScreen.id) {
            localStorage.removeItem(`autosave_${this.serviceId}_${currentScreen.id}`);
          }

          if (response && response.completed) {
            if (this.serviceId) {
               this.draftService.deleteDraft(this.serviceId);
            }
            this.stateService.clearState();
            this.loading = false;
            this.cdr.detectChanges();
            return;
          }

          if (response && response.next_screen && response.next_screen.id) {
            this.stateService.setScreen(response.next_screen);

            if (this.serviceId) {
              this.draftService.saveDraft(this.serviceId, response.next_screen, {});
            }

            const nextScreen = response.next_screen;
            if (this.serviceId) {
              const autoSaveKey = `autosave_${this.serviceId}_${nextScreen.id}`;
              const savedAnswersStr = localStorage.getItem(autoSaveKey);
              if (savedAnswersStr) {
                try {
                  const savedAnswers = JSON.parse(savedAnswersStr);
                  this.stateService.restoreAnswers(savedAnswers);
                  this.draftService.saveDraft(this.serviceId, nextScreen, savedAnswers);
                } catch (e) {
                  console.error('Failed to parse autosave data', e);
                }
              }
            }

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