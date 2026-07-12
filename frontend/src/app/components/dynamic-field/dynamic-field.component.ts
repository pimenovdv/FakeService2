import { Component, Input, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { StateService } from '../../services/state';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent implements OnInit, OnDestroy {
  @Input() componentDef!: ComponentDef;

  private stateService = inject(StateService);
  private subscription = new Subscription();

  isVisible = true;
  isDisabled = false;

  ngOnInit() {
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
      this.isVisible = this.stateService.evaluateCondition(this.componentDef.showIf);
    } else {
      this.isVisible = this.componentDef.hidden !== true;
    }

    if (this.componentDef.disableIf) {
      this.isDisabled = this.stateService.evaluateCondition(this.componentDef.disableIf);
      // We also update the definition to maintain compatibility with specific controls
      // but creating a new reference to ensure change detection triggers if needed,
      // or specific controls could rely on a new input. For now, since BaseControl binds to def.disabled:
      this.componentDef = { ...this.componentDef, disabled: this.isDisabled };
    } else {
      this.isDisabled = this.componentDef.disabled === true;
    }
  }
}
