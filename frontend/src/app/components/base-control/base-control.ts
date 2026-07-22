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

  get maxLengthRule(): number | null {
    if (this.def && this.def.validations) {
      const rule = this.def.validations.find(r => r.type === 'maxLength');
      if (rule && rule.value !== undefined) {
        return Number(rule.value);
      }
    }
    return null;
  }

  get currentLength(): number {
    if (this.value === null || this.value === undefined) {
      return 0;
    }
    return this.value.toString().length;
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
