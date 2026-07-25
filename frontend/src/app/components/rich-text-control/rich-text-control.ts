import { Component, Input } from '@angular/core';
import { BaseControl } from '../base-control/base-control';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { QuillEditorComponent } from 'ngx-quill';

@Component({
  selector: 'app-rich-text-control',
  standalone: true,
  imports: [CommonModule, FormsModule, QuillEditorComponent],
  templateUrl: './rich-text-control.html',
  styleUrl: './rich-text-control.scss',
})
export class RichTextControl extends BaseControl {
  @Input() override value: string = '';

  constructor() {
    super();
  }
}
