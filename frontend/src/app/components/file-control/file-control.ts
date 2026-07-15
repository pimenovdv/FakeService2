import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-file-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-control.html'
})
export class FileControlComponent extends BaseControl implements OnInit, OnDestroy {

  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      if (this.def.multiple) {
        // Collect file objects if multiple
        const filesArray = Array.from(input.files);
        this.onValueChange(filesArray);
      } else {
        // Collect single file if not multiple
        const file = input.files[0];
        this.onValueChange(file ? [file] : null); // Still sending array for consistency or single file if preferred, usually single file is sent as is. Wait, the python agent tests for "multiple" and "accept".
        // Let's send the single file if not multiple, or array if multiple.
        this.onValueChange(file || null);
      }
    } else {
      this.onValueChange(null);
    }
  }
}
