import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';
import { forkJoin, Observable, of } from 'rxjs';
import { catchError, map, filter } from 'rxjs/operators';
import { HttpEvent, HttpEventType, HttpResponse } from '@angular/common/http';

@Component({
  selector: 'app-file-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-control.html'
})
export class FileControlComponent extends BaseControl implements OnInit, OnDestroy {
  isUploading = false;
  uploadError: string | null = null;
  uploadProgress: Record<string, number> = {};
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

      this.uploadProgress = {};
      filesArray.forEach(f => this.uploadProgress[f.name] = 0);

      if (this.def.multiple) {
        const uploadRequests = filesArray.map(file =>
          this.apiService.uploadFile(file).pipe(
            map((event: HttpEvent<any>) => {
              if (event.type === HttpEventType.UploadProgress) {
                if (event.total) {
                  this.uploadProgress[file.name] = Math.round(100 * event.loaded / event.total);
                }
              }
              return event;
            }),
            filter((event: HttpEvent<any>) => event.type === HttpEventType.Response),
            map((event: any) => (event as HttpResponse<any>).body),
            catchError(err => {
              console.error(`File upload failed for ${file.name}`, err);
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
            next: (event: HttpEvent<any>) => {
              if (event.type === HttpEventType.UploadProgress) {
                if (event.total) {
                  this.uploadProgress[file.name] = Math.round(100 * event.loaded / event.total);
                }
              } else if (event.type === HttpEventType.Response) {
                this.isUploading = false;
                this.onValueChange((event as HttpResponse<any>).body);
              }
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
      this.uploadProgress = {};
      this.onValueChange(null);
    }
  }
}
