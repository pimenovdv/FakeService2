import { Directive, EventEmitter, Input, Output, OnInit, OnDestroy, inject } from '@angular/core';
import { Subscription } from 'rxjs';
import { StateService } from '../../services/state';
import { ComponentDef, ValidationRule } from '../../models/screen.model';

@Directive()
export abstract class BaseControl implements OnInit, OnDestroy {
  @Input() def!: ComponentDef;
  @Input() value: any;
  @Output() valueChange = new EventEmitter<any>();
  @Output() isValidChange = new EventEmitter<boolean>();

  protected stateService = inject(StateService);
  protected sub = new Subscription();

  ngOnInit() {
    this.validate();
    this.isValidChange.emit(this.isValid);

    this.sub.add(
      this.stateService.submitAttempted$.subscribe(attempted => {
        if (attempted) {
          this.touched = true;
          this.validate();
          this.isValidChange.emit(this.isValid);
        }
      })
    );
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
    if (this.def && this.def.id) { this.stateService.setValidation(this.def.id, true); } // if destroyed, consider it valid so it doesn't block
  }

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
          if (this.value !== null && this.value !== undefined && this.value !== '' && rule.value !== undefined) {
            const v = isNaN(Date.parse(this.value)) ? Number(this.value) : Date.parse(this.value);
            const r = isNaN(Date.parse(rule.value)) ? Number(rule.value) : Date.parse(rule.value);
            if (v < r) {
              this.errors.push(rule.message || `Minimum value is ${rule.value}`);
            }
          }
          break;

        case 'max':
          if (this.value !== null && this.value !== undefined && this.value !== '' && rule.value !== undefined) {
            const v = isNaN(Date.parse(this.value)) ? Number(this.value) : Date.parse(this.value);
            const r = isNaN(Date.parse(rule.value)) ? Number(rule.value) : Date.parse(rule.value);
            if (v > r) {
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
        case 'maxSize':
          if (this.value && this.value.size !== undefined && rule.value !== undefined) {
            if (this.value.size > Number(rule.value)) {
              this.errors.push(rule.message || `File size must be less than ${rule.value} bytes`);
            }
          }
          break;
        case 'allowedTypes':
          if (this.value && this.value.type !== undefined && rule.value !== undefined) {
            const types = Array.isArray(rule.value) ? rule.value : [rule.value];
            if (!types.includes(this.value.type)) {
              this.errors.push(rule.message || `File type ${this.value.type} is not allowed`);
            }
          }
          break;
      }
    }
  }
}
