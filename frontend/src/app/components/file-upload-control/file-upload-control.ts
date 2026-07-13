import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-file-upload-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './file-upload-control.html',
  styleUrls: ['./file-upload-control.scss']
})
export class FileUploadControlComponent extends BaseControl {
  selectedFileName: string | null = null;
  fileError: string | null = null;

  onFileSelected(event: any) {
    this.touched = true;
    this.fileError = null;
    const file: File = event.target.files[0];

    if (!file) {
      this.selectedFileName = null;
      this.onValueChange(null);
      return;
    }

    // Check size constraint locally if it exists to prevent reading huge files
    // The main validation engine will also check it later, but doing it here saves RAM
    if (this.def.validations) {
      const sizeRule = this.def.validations.find(r => r.type === 'maxSize');
      if (sizeRule && file.size > Number(sizeRule.value)) {
        this.fileError = sizeRule.message || `File size must be less than ${sizeRule.value} bytes`;
        this.selectedFileName = file.name;
        this.onValueChange(null);
        return;
      }

      const typeRule = this.def.validations.find(r => r.type === 'allowedTypes');
      if (typeRule) {
         // Expect allowedTypes value to be an array of strings e.g., ['image/png', 'application/pdf']
         const types = Array.isArray(typeRule.value) ? typeRule.value : [typeRule.value];
         if (!types.includes(file.type)) {
            this.fileError = typeRule.message || `File type ${file.type} is not allowed`;
            this.selectedFileName = file.name;
            this.onValueChange(null);
            return;
         }
      }
    }

    this.selectedFileName = file.name;
    const reader = new FileReader();
    reader.onload = () => {
      const base64String = reader.result as string;
      this.onValueChange({
        filename: file.name,
        type: file.type,
        size: file.size,
        data: base64String
      });
    };
    reader.onerror = () => {
      this.fileError = 'Error reading file';
      this.onValueChange(null);
    };
    reader.readAsDataURL(file);
  }
}
