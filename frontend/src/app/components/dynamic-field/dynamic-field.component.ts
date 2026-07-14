import { Component, Input, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { CheckboxControlComponent } from '../checkbox-control/checkbox-control';
import { RadioControlComponent } from '../radio-control/radio-control';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent, CheckboxControlComponent, RadioControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent implements OnInit, OnDestroy {
  @Input() componentDef!: ComponentDef;

  isHidden = false;
  isDisabled = false;
  value: any;

  private stateService = inject(StateService);
  private subscription = new Subscription();
  private cdr = inject(ChangeDetectorRef);

  ngOnInit() {
    this.isHidden = this.componentDef.hidden || false;
    this.isDisabled = this.componentDef.disabled || false;

    this.value = this.stateService.getAllAnswers()[this.componentDef.id];

    this.subscription.add(
      this.stateService.answers$.subscribe(() => {
        this.evaluateConditions();
      })
    );
  }

  ngOnDestroy() {
    this.subscription.unsubscribe();
  }


  onValueChange(val: any) {
    this.value = val;
    this.stateService.setAnswer(this.componentDef.id, val);
  }

  onValidChange(valid: boolean) {
    this.stateService.setValidation(this.componentDef.id, valid);
  }

  private evaluateConditions() {
    let changed = false;
    if (this.componentDef.showIf) {
      const isHidden = !this.stateService.evaluateCondition(this.componentDef.showIf);
      if (this.isHidden !== isHidden) {
        this.isHidden = isHidden;
        this.componentDef.hidden = this.isHidden;
        changed = true;
      }
    }

    if (this.componentDef.disableIf) {
      const isDisabled = this.stateService.evaluateCondition(this.componentDef.disableIf);
      if (this.isDisabled !== isDisabled) {
        this.isDisabled = isDisabled;
        this.componentDef.disabled = this.isDisabled;
        changed = true;
      }
    }

    if (changed) {
      this.cdr.detectChanges();
    }
  }
}
