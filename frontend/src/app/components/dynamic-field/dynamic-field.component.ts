import { Component, Input, OnInit, OnDestroy, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { CheckboxControlComponent } from '../checkbox-control/checkbox-control';
import { RadioControlComponent } from '../radio-control/radio-control';
import { DatepickerControlComponent } from '../datepicker-control/datepicker-control';
import { TextareaControlComponent } from '../textarea-control/textarea-control';
import { FileControlComponent } from '../file-control/file-control';
import { NumberControlComponent } from '../number-control/number-control';
import { PasswordControlComponent } from '../password-control/password-control';
import { SliderControlComponent } from '../slider-control/slider-control';
import { ColorControlComponent } from '../color-control/color-control';
import { TimeControlComponent } from '../time-control/time-control';
import { ToggleControlComponent } from '../toggle-control/toggle-control';
import { RatingControlComponent } from '../rating-control/rating-control';
import { StepperControlComponent } from '../stepper-control/stepper-control';
import { CurrencyControlComponent } from '../currency-control/currency-control';
import { TagsControlComponent } from '../tags-control/tags-control';
import { EmailControlComponent } from '../email-control/email-control';
import { PhoneControlComponent } from '../phone-control/phone-control';
import { UrlControlComponent } from '../url-control/url-control.component';
import { MonthControlComponent } from '../month-control/month-control.component';
import { SearchControlComponent } from '../search-control/search-control.component';
import { WeekControlComponent } from '../week-control/week-control.component';
import { DatetimeControlComponent } from '../datetime-control/datetime-control.component';
import { MultiselectControlComponent } from '../multiselect-control/multiselect-control';
import { AutocompleteControlComponent } from '../autocomplete-control/autocomplete-control';
import { ButtonGroupControlComponent } from '../button-group-control/button-group-control.component';
import { CaptchaControlComponent } from '../captcha-control/captcha-control.component';
import { ProgressControlComponent } from '../progress-control/progress-control';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent, CheckboxControlComponent, RadioControlComponent, DatepickerControlComponent, TextareaControlComponent, FileControlComponent, NumberControlComponent, PasswordControlComponent, SliderControlComponent, ColorControlComponent, TimeControlComponent, ToggleControlComponent, RatingControlComponent, StepperControlComponent, CurrencyControlComponent, TagsControlComponent, EmailControlComponent, PhoneControlComponent, UrlControlComponent, MonthControlComponent, SearchControlComponent, WeekControlComponent, DatetimeControlComponent, MultiselectControlComponent, AutocompleteControlComponent, ButtonGroupControlComponent, CaptchaControlComponent, ProgressControlComponent],
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
