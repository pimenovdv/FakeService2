import { Component, Input, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent implements OnInit, OnDestroy {
  @Input() componentDef!: ComponentDef;

  isHidden = false;
  isDisabled = false;
  private lastReportedValidity = true;

  private stateService = inject(StateService);
  private subscription = new Subscription();

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

  onValueChange(value: any) {
    this.stateService.setAnswer(this.componentDef.id, value);
  }

  onValidityChange(isValid: boolean) {
    this.lastReportedValidity = isValid;
    this.updateValidationState();
  }

  private updateValidationState() {
    const effectiveValidity = (this.isHidden || this.isDisabled) ? true : this.lastReportedValidity;
    this.stateService.setValidationState(this.componentDef.id, effectiveValidity);
  }

  private evaluateConditions() {
    let changed = false;

    if (this.componentDef.showIf) {
      const newHidden = !this.stateService.evaluateCondition(this.componentDef.showIf);
      if (this.isHidden !== newHidden) {
        this.isHidden = newHidden;
        this.componentDef.hidden = this.isHidden;
        changed = true;
      }
    }

    if (this.componentDef.disableIf) {
      const newDisabled = this.stateService.evaluateCondition(this.componentDef.disableIf);
      if (this.isDisabled !== newDisabled) {
        this.isDisabled = newDisabled;
        this.componentDef.disabled = this.isDisabled;
        changed = true;
      }
    }

    if (changed) {
      this.updateValidationState();
    }
  }
}
