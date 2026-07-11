import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';

@Component({
  selector: 'app-combobox',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './combobox.html',
  styleUrls: ['./combobox.scss']
})
export class ComboBoxComponent extends BaseControl implements OnInit {
  options: { value: any, label: string }[] = [];
  loading = false;
  errorFetching = false;

  constructor(private apiService: ApiService) {
    super();
  }

  ngOnInit() {
    if (this.def.options) {
      this.options = [...this.def.options];
    } else if (this.def.restMetadata) {
      this.loading = true;
      this.apiService.dynamicCall(this.def.restMetadata).subscribe({
        next: (data) => {
          this.options = Array.isArray(data) ? data : (data.options || []);
          this.loading = false;
        },
        error: (err) => {
          console.error(`Error fetching options for ${this.def.id}`, err);
          this.errorFetching = true;
          this.loading = false;
        }
      });
    }
  }
}
