import { Component, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { DynamicFieldComponent } from '../dynamic-field/dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';

@Component({
  selector: 'app-data-table-control',
  standalone: true,
  imports: [CommonModule, FormsModule, forwardRef(() => DynamicFieldComponent)],
  templateUrl: './data-table-control.component.html',
  styleUrls: ['./data-table-control.component.css']
})
export class DataTableControlComponent extends BaseControl {
  get columns(): ComponentDef[] {
    return this.def.components || [];
  }

  get rows(): any[] {
    return Array.isArray(this.value) ? this.value : [];
  }

  isRequired(): boolean {
    return this.def.validations?.some(v => v.type === 'required') || false;
  }

  addRow() {
    const newRow: any = {};
    this.columns.forEach(col => {
      newRow[col.id] = null; // Initialize with null or default value
    });

    const updatedValue = [...this.rows, newRow];
    this.onValueChange(updatedValue);
  }

  removeRow(index: number) {
    const updatedValue = [...this.rows];
    updatedValue.splice(index, 1);
    this.onValueChange(updatedValue);
  }

  onCellChange(index: number, colId: string, newValue: any) {
    const updatedValue = [...this.rows];
    updatedValue[index] = {
      ...updatedValue[index],
      [colId]: newValue
    };
    this.onValueChange(updatedValue);
  }
}
