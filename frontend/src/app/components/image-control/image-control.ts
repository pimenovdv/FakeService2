import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-image-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './image-control.html'
})
export class ImageControlComponent extends BaseControl {
}
