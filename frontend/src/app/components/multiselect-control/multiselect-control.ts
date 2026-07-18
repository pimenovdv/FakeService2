import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-multiselect-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './multiselect-control.html',
  styleUrls: ['./multiselect-control.scss']
})
export class MultiselectControlComponent extends BaseControl implements OnInit, OnDestroy {
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
  }

  private loadDynamicOptions() {
    if (!this.def.restMetadata) return;

    this.loadingOptions = true;
    this.optionsError = null;

    this.apiService.dynamicCall(this.def.restMetadata).subscribe({
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
