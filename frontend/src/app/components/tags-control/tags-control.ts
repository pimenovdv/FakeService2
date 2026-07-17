import { Component, forwardRef, OnInit, OnDestroy, ChangeDetectionStrategy, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-tags-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './tags-control.html',
  styleUrls: ['./tags-control.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: BaseControl,
      useExisting: forwardRef(() => TagsControlComponent)
    }
  ]
})
export class TagsControlComponent extends BaseControl implements OnInit, OnDestroy {
  tags: string[] = [];
  inputValue: string = '';

  private cdr = inject(ChangeDetectorRef);

  constructor() {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();
    if (this.value) {
      if (Array.isArray(this.value)) {
        this.tags = [...this.value];
      } else if (typeof this.value === 'string') {
        this.tags = this.value.split(',').map(t => t.trim()).filter(t => t);
      }
    } else {
        this.tags = [];
    }
  }

  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  onKeyDown(event: KeyboardEvent) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      this.addTag();
    }
  }

  addTag() {
    const newTag = this.inputValue.trim();
    if (newTag) {
        if (!this.tags.includes(newTag)) {
             this.tags.push(newTag);
             this.updateModel();
        }
    }
    this.inputValue = '';
    this.cdr.markForCheck();
  }

  removeTag(index: number) {
    if (!this.def?.disabled) {
      this.tags.splice(index, 1);
      this.updateModel();
      this.cdr.markForCheck();
    }
  }

  onBlur() {
     this.touched = true;
     this.addTag(); // Add tag on blur too, like some tag inputs
     this.validate();
  }

  private updateModel() {
    this.onValueChange([...this.tags]);
  }

  override validate() {
    this.errors = [];
    let isValid = true;

    if (this.def?.validations) {
      for (const rule of this.def.validations) {
        if (rule.type === 'required' && this.tags.length === 0) {
          isValid = false;
          this.errors.push(rule.message || 'At least one tag is required');
        }
      }
    }

    this.isValidChange.emit(isValid);
    this.cdr.markForCheck();
  }
}
