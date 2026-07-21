import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-combobox-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './combobox-control.html',
  styleUrls: ['./combobox-control.scss']
})
export class ComboboxControlComponent extends BaseControl implements OnInit, OnDestroy {
  private apiService = inject(ApiService);

  options: any[] = [];
  loadingOptions = false;
  optionsError: string | null = null;

  override ngOnInit() {
    super.ngOnInit();
    if (this.def.options) {
      this.options = this.def.options;
    } else if (this.def.restMetadata) {
      this.loadDynamicOptions();
    }

    if (this.def.dependsOn && this.def.dependsOn.length > 0) {
      this.sub.add(
        this.stateService.answerChanges$.subscribe(change => {
          if (this.def.dependsOn?.includes(change.componentId)) {
             if (this.def.restMetadata) {
                this.loadDynamicOptions();
             }
          }
        })
      );
    }
  }

  private loadDynamicOptions() {
    if (!this.def.restMetadata) return;

    this.loadingOptions = true;
    this.optionsError = null;

    // Map dependent answers to params if they are defined
    let params = { ...this.def.restMetadata.params };
    if (this.def.dependsOn) {
      const allAnswers = this.stateService.getAllAnswers();
      this.def.dependsOn.forEach(depId => {
        if (allAnswers[depId] !== undefined) {
          params[depId] = allAnswers[depId];
        }
      });
    }

    const modifiedMetadata = { ...this.def.restMetadata, params };

    this.apiService.dynamicCall(modifiedMetadata).subscribe({
      next: (data: any[]) => {
        this.options = data;
        this.loadingOptions = false;
      },
      error: (err) => {
        console.error('Failed to load dynamic options', err);
        this.optionsError = 'Failed to load options';
        this.loadingOptions = false;
      }
    });
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
