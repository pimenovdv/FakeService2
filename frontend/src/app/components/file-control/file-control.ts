import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';
import { forkJoin, Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Component({
  selector: 'app-file-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-control.html'
})
export class FileControlComponent extends BaseControl implements OnInit, OnDestroy {
  isUploading = false;
  uploadError: string | null = null;
  private apiService = inject(ApiService);

  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }

  onFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    this.uploadError = null;

    if (input.files && input.files.length > 0) {
      this.isUploading = true;
      const filesArray = Array.from(input.files);

      if (this.def.multiple) {
        const uploadRequests = filesArray.map(file =>
          this.apiService.uploadFile(file).pipe(
            catchError(err => {
              console.error('File upload failed', err);
              return of(null); // Return null for failed uploads to handle them gracefully
            })
          )
        );

        this.sub.add(
          forkJoin(uploadRequests).subscribe(responses => {
            this.isUploading = false;
            const successfulUploads = responses.filter(r => r !== null);

            if (successfulUploads.length === 0 && filesArray.length > 0) {
                this.uploadError = "Upload failed for all selected files.";
                this.onValueChange(null);
            } else {
                if (successfulUploads.length < filesArray.length) {
                   this.uploadError = `Only ${successfulUploads.length} out of ${filesArray.length} files uploaded successfully.`;
                }
                this.onValueChange(successfulUploads);
            }
          })
        );
      } else {
        const file = filesArray[0];
        this.sub.add(
          this.apiService.uploadFile(file).subscribe({
            next: (response) => {
              this.isUploading = false;
              this.onValueChange(response);
            },
            error: (err) => {
              console.error('File upload failed', err);
              this.isUploading = false;
              this.uploadError = 'File upload failed. Please try again.';
              this.onValueChange(null);
            }
          })
        );
      }
    } else {
      this.onValueChange(null);
    }
  }
}
