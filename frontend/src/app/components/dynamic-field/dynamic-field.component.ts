import { Component, Input, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { StateService } from '../../services/state';
import { BaseControl } from '../base-control/base-control';
import { ViewChild } from '@angular/core';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent implements OnInit, OnDestroy {
  @Input() componentDef!: ComponentDef;
  @ViewChild('innerControl') innerControl!: BaseControl;

  isHidden = false;
  isDisabled = false;

  private stateService = inject(StateService);
  private subscription = new Subscription();

  get value(): any {
    return this.stateService.getAnswer(this.componentDef.id);
  }

  onValueChange(newValue: any) {
    this.stateService.setAnswer(this.componentDef.id, newValue);
  }

  validate(): boolean {
    if (this.isHidden || this.isDisabled) {
      return true;
    }
    if (this.innerControl) {
      this.innerControl.touched = true;
      this.innerControl.validate();
      return this.innerControl.isValid;
    }
    return true; // If no control to validate, consider valid
  }

  ngOnInit() {
    this.isHidden = this.componentDef.hidden || false;
    this.isDisabled = this.componentDef.disabled || false;

    this.subscription.add(
      this.stateService.answers$.subscribe(() => {
        this.evaluateConditions();
      })
    );
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }

  private evaluateConditions() {
    if (this.componentDef.showIf) {
      this.isHidden = !this.stateService.evaluateCondition(this.componentDef.showIf);
      this.componentDef.hidden = this.isHidden;
    }

    if (this.componentDef.disableIf) {
      this.isDisabled = this.stateService.evaluateCondition(this.componentDef.disableIf);
      // We also update the componentDef so child components receive the updated disabled state
      this.componentDef.disabled = this.isDisabled;
    }
  }
}
