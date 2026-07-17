import { Component, ChangeDetectionStrategy, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-rating-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './rating-control.html',
  styleUrls: ['./rating-control.css'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class RatingControlComponent extends BaseControl {
  stars = [1, 2, 3, 4, 5];
  hoverValue = 0;

  constructor(private cdr: ChangeDetectorRef) {
    super();
  }

  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  setRating(rating: number) {
    if (!this.def?.disabled && this.def?.disabled !== true) {
      this.onValueChange(rating);
    }
  }

  setHover(rating: number) {
    if (!this.def?.disabled && this.def?.disabled !== true) {
      this.hoverValue = rating;
      this.cdr.markForCheck();
    }
  }

  clearHover() {
    if (!this.def?.disabled && this.def?.disabled !== true) {
      this.hoverValue = 0;
      this.cdr.markForCheck();
    }
  }
}
