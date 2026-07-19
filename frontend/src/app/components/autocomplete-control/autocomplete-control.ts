import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-autocomplete-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './autocomplete-control.html',
  styleUrls: ['./autocomplete-control.css']
})
export class AutocompleteControlComponent extends BaseControl implements OnInit {
  options: any[] = [];
  datalistId: string = '';
  private http = inject(HttpClient);

  override ngOnInit(): void {
    super.ngOnInit();
    this.datalistId = `datalist-${this.def?.id}`;
    if (this.def?.options) {
      this.options = this.def.options;
    } else if (this.def?.restMetadata) {
      this.loadOptions();
    }
  }

  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  private loadOptions() {
    if (!this.def?.restMetadata) return;
    const { endpoint, method, params } = this.def.restMetadata;
    const options = params ? { params } : {};

    if (method === 'GET') {
      this.http.get<any[]>(endpoint, options).subscribe({
        next: (res) => this.options = res,
        error: (err) => console.error('Error loading autocomplete options', err)
      });
    } else if (method === 'POST') {
      this.http.post<any[]>(endpoint, params || {}).subscribe({
        next: (res) => this.options = res,
        error: (err) => console.error('Error loading autocomplete options', err)
      });
    }
  }
}
