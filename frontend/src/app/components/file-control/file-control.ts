import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';
import { ApiService } from '../../services/api';
import { forkJoin, Observable, of } from 'rxjs';
import { catchError, map, filter } from 'rxjs/operators';
import { HttpEventType, HttpResponse, HttpEvent } from '@angular/common/http';

@Component({
  selector: 'app-file-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './file-control.html'
})
export class FileControlComponent extends BaseControl implements OnInit, OnDestroy {
  isUploading = false;
  uploadError: string | null = null;
  uploadProgresses: { [key: string]: number } = {};
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
    this.uploadProgresses = {};

    if (input.files && input.files.length > 0) {
      this.isUploading = true;
      const filesArray = Array.from(input.files);

      if (this.def.multiple) {
        const uploadRequests = filesArray.map(file => {
          this.uploadProgresses[file.name] = 0;
          return this.apiService.uploadFile(file).pipe(
            map((event: HttpEvent<any>) => {
              if (event.type === HttpEventType.UploadProgress && event.total) {
                this.uploadProgresses[file.name] = Math.round(100 * event.loaded / event.total);
                return null;
              } else if (event.type === HttpEventType.Response) {
                return event.body;
              }
              return null;
            }),
            filter((res): res is any => res !== null),
            catchError(err => {
              console.error(`File upload failed for ${file.name}`, err);
              return of(null); // Return null for failed uploads to handle them gracefully
            })
          );
        });

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
        this.uploadProgresses[file.name] = 0;
        this.sub.add(
          this.apiService.uploadFile(file).subscribe({
            next: (event: HttpEvent<any>) => {
              if (event.type === HttpEventType.UploadProgress && event.total) {
                this.uploadProgresses[file.name] = Math.round(100 * event.loaded / event.total);
              } else if (event.type === HttpEventType.Response) {
                this.isUploading = false;
                this.onValueChange(event.body);
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
      this.onValueChange(null);
    }
  }
}
