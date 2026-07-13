import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';
import { catchError, of } from 'rxjs';

@Component({
  selector: 'app-combobox-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './combobox-control.html',
  styleUrls: ['./combobox-control.scss']
})
export class ComboboxControlComponent extends BaseControl implements OnInit {
  private apiService = inject(ApiService);

  options: any[] = [];
  loadingOptions = false;
  optionsError: string | null = null;

  ngOnInit() {
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

    this.apiService.dynamicCall(this.def.restMetadata).pipe(
      catchError((err) => {
        console.error('Failed to load dynamic options', err);
        this.optionsError = 'Failed to load options';
        this.loadingOptions = false;
        return of([]);
      })
    ).subscribe({
      next: (data: any[]) => {
        this.options = data;
        this.loadingOptions = false;
      }
    });
  }
}
