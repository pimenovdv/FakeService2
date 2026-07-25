import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FileControlComponent } from './file-control';
import { StateService } from '../../services/state';
import { ApiService } from '../../services/api';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { of, throwError } from 'rxjs';
import { HttpEventType, HttpResponse } from '@angular/common/http';

describe('FileControlComponent', () => {
  let component: FileControlComponent;
  let fixture: ComponentFixture<FileControlComponent>;
  let stateService: StateService;
  let apiServiceSpy: any;

  const mockDef: ComponentDef = {
    id: 'test-file',
    type: 'file',
    label: 'Upload File',
    accept: 'image/*',
    multiple: true
  };

  beforeEach(async () => {
    apiServiceSpy = {
      uploadFile: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [FileControlComponent],
      providers: [
        StateService,
        { provide: ApiService, useValue: apiServiceSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(FileControlComponent);
    component = fixture.componentInstance;
    component.def = mockDef;
    stateService = TestBed.inject(StateService);

    // Create spy using Vitest vi.spyOn
    vi.spyOn(stateService, 'setAnswer');

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render file input with correct attributes', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');
    expect(inputElement).toBeTruthy();
    expect(inputElement.getAttribute('id')).toBe('test-file');
    expect(inputElement.getAttribute('accept')).toBe('image/*');
    expect(inputElement.hasAttribute('multiple')).toBe(true);
  });

  it('should default accept to */* if not provided', () => {
    fixture.componentRef.setInput('def', { ...mockDef, accept: undefined, multiple: false });
    fixture.detectChanges();
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');
    expect(inputElement.getAttribute('accept')).toBe('*/*');
    expect(inputElement.hasAttribute('multiple')).toBe(false);
  });

  it('should handle file selection for multiple files', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    apiServiceSpy.uploadFile.mockImplementation((file: File) => {
        return of(
          { type: HttpEventType.UploadProgress, loaded: 50, total: 100 },
          new HttpResponse({ body: { file_id: `id_${file.name}`, url: `/mock-uploads/id_${file.name}/${file.name}`, filename: file.name } })
        );
    });

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt'), new File([''], 'file2.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(apiServiceSpy.uploadFile).toHaveBeenCalledTimes(2);
    expect(component.value.length).toBe(2);
    expect(component.value[0].filename).toBe('file1.txt');
    expect(component.value[1].filename).toBe('file2.txt');
    expect(component.uploadProgress['file1.txt']).toBe(50);
    expect(component.uploadProgress['file2.txt']).toBe(50);
  });

  it('should handle file selection for single file', () => {
    fixture.componentRef.setInput('def', { ...mockDef, multiple: false });
    fixture.detectChanges();

    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    apiServiceSpy.uploadFile.mockImplementation((file: File) => {
        return of(
          { type: HttpEventType.UploadProgress, loaded: 100, total: 100 },
          new HttpResponse({ body: { file_id: `id_${file.name}`, url: `/mock-uploads/id_${file.name}/${file.name}`, filename: file.name } })
        );
    });

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(apiServiceSpy.uploadFile).toHaveBeenCalledTimes(1);
    expect(component.value.filename).toBe('file1.txt');
    expect(component.uploadProgress['file1.txt']).toBe(100);
  });

  it('should handle upload error for single file', () => {
    fixture.componentRef.setInput('def', { ...mockDef, multiple: false });
    fixture.detectChanges();

    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    apiServiceSpy.uploadFile.mockReturnValue(throwError(() => new Error('Upload failed')));

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(apiServiceSpy.uploadFile).toHaveBeenCalledTimes(1);
    expect(component.value).toBeNull();
    expect(component.uploadError).toBe('File upload failed. Please try again.');
  });

  it('should handle partial upload success for multiple files', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    apiServiceSpy.uploadFile.mockImplementation((file: File) => {
        if (file.name === 'file1.txt') {
            return of(new HttpResponse({ body: { file_id: `id_${file.name}`, url: `/mock-uploads/id_${file.name}/${file.name}`, filename: file.name } }));
        } else {
            return throwError(() => new Error('Upload failed'));
        }
    });

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt'), new File([''], 'file2.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(apiServiceSpy.uploadFile).toHaveBeenCalledTimes(2);
    expect(component.value.length).toBe(1);
    expect(component.value[0].filename).toBe('file1.txt');
    expect(component.uploadError).toBe('Only 1 out of 2 files uploaded successfully.');
  });

  it('should handle full upload failure for multiple files', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    apiServiceSpy.uploadFile.mockReturnValue(throwError(() => new Error('Upload failed')));

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt'), new File([''], 'file2.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(apiServiceSpy.uploadFile).toHaveBeenCalledTimes(2);
    expect(component.value).toBeNull();
    expect(component.uploadError).toBe('Upload failed for all selected files.');
  });

  it('should allow removing a file', () => {
    component.value = [
      { filename: 'file1.txt' },
      { filename: 'file2.txt' },
      { filename: 'file3.txt' }
    ];

    component.removeFile(1);

    expect(component.value.length).toBe(2);
    expect(component.value[0].filename).toBe('file1.txt');
    expect(component.value[1].filename).toBe('file3.txt');
  });

  it('should set value to null if removing the last file', () => {
    component.value = [{ filename: 'file1.txt' }];
    component.removeFile(0);
    expect(component.value).toBeNull();
  });

  it('should handle drag and drop to reorder files', () => {
    component.value = [
      { filename: 'file1.txt' },
      { filename: 'file2.txt' },
      { filename: 'file3.txt' }
    ];

    // Simulate drag start on index 0
    const dragStartEvent = new Event('dragstart') as any;
    dragStartEvent.dataTransfer = {
      setData: vi.fn(),
      effectAllowed: ''
    };
    component.onDragStart(dragStartEvent, 0);
    expect(component.draggedIndex).toBe(0);

    // Simulate drop on index 2
    const dropEvent = new Event('drop') as any;
    dropEvent.preventDefault = vi.fn();
    component.onDrop(dropEvent, 2);

    expect(component.value.length).toBe(3);
    expect(component.value[0].filename).toBe('file2.txt');
    expect(component.value[1].filename).toBe('file3.txt');
    expect(component.value[2].filename).toBe('file1.txt');
    expect(component.draggedIndex).toBeNull();
  });

  it('should append files on subsequent uploads when multiple is true', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    // Initial state
    component.value = [{ filename: 'existing.txt' }];

    apiServiceSpy.uploadFile.mockImplementation((file: File) => {
        return of(
          { type: HttpEventType.UploadProgress, loaded: 100, total: 100 },
          new HttpResponse({ body: { file_id: `id_${file.name}`, url: `/mock-uploads/id_${file.name}/${file.name}`, filename: file.name } })
        );
    });

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'new.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(component.value.length).toBe(2);
    expect(component.value[0].filename).toBe('existing.txt');
    expect(component.value[1].filename).toBe('new.txt');
  });

  it('should handle null files properly', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    // Clear the files property
    Object.defineProperty(inputElement, 'files', {
        value: null,
        writable: true
    });

    inputElement.dispatchEvent(new Event('change'));
    expect(component.value).toBeNull();
  });
});
