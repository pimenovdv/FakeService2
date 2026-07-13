import { Directive, EventEmitter, Input, Output } from '@angular/core';
import { ComponentDef, ValidationRule } from '../../models/screen.model';

@Directive()
export abstract class BaseControl {
  @Input() def!: ComponentDef;
  @Input() value: any;
  @Output() valueChange = new EventEmitter<any>();
  @Output() isValidChange = new EventEmitter<boolean>();

  errors: string[] = [];
  touched = false;

  get isValid(): boolean {
    return this.errors.length === 0;
  }

  onValueChange(newValue: any) {
    this.value = newValue;
    this.touched = true;
    this.validate();
    this.valueChange.emit(this.value);
    this.isValidChange.emit(this.isValid);
  }

  validate() {
    this.errors = [];
    if (!this.def || !this.def.validations) {
      return;
    }

    if (this.def.disabled || this.def.hidden) {
      return; // Disabled or hidden components are always valid
    }

    for (const rule of this.def.validations) {
      switch (rule.type) {
        case 'required':
          if (this.value === null || this.value === undefined || this.value === '') {
            this.errors.push(rule.message || 'This field is required');
          }
          break;
        case 'regex':
          if (this.value && rule.value) {
            const regex = new RegExp(rule.value);
            if (!regex.test(this.value.toString())) {
              this.errors.push(rule.message || 'Invalid format');
            }
          }
          break;
        case 'min':
          if (this.value !== null && this.value !== undefined && rule.value !== undefined) {
            if (Number(this.value) < Number(rule.value)) {
              this.errors.push(rule.message || `Minimum value is ${rule.value}`);
            }
          }
          break;
        case 'max':
          if (this.value !== null && this.value !== undefined && rule.value !== undefined) {
            if (Number(this.value) > Number(rule.value)) {
              this.errors.push(rule.message || `Maximum value is ${rule.value}`);
            }
          }
          break;
        case 'minLength':
          if (this.value && rule.value !== undefined) {
            if (this.value.toString().length < Number(rule.value)) {
              this.errors.push(rule.message || `Minimum length is ${rule.value}`);
            }
          }
          break;
        case 'maxLength':
          if (this.value && rule.value !== undefined) {
            if (this.value.toString().length > Number(rule.value)) {
              this.errors.push(rule.message || `Maximum length is ${rule.value}`);
            }
          }
          break;
      }
    }
  }
}
