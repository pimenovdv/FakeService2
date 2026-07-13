import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FileUploadControlComponent } from './file-upload-control';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach, vi } from 'vitest';
import { FormsModule } from '@angular/forms';

describe('FileUploadControlComponent', () => {
  let component: FileUploadControlComponent;
  let fixture: ComponentFixture<FileUploadControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FileUploadControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(FileUploadControlComponent);
    component = fixture.componentInstance;
    component.def = { id: 'test-file', type: 'file', label: 'Test File' } as ComponentDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should handle file selection, convert to base64 and emit', () => {
    const valueChangeSpy = vi.spyOn(component.valueChange, 'emit');

    const file = new File(['file content'], 'test.txt', { type: 'text/plain' });
    const event = { target: { files: [file] } };

    // Mock FileReader
    const mockFileReader = {
      readAsDataURL: vi.fn().mockImplementation(function(this: any, blob) {
        this.result = 'data:text/plain;base64,ZmlsZSBjb250ZW50';
        this.onload();
      })
    };
    vi.stubGlobal('FileReader', function() { return mockFileReader; });

    component.onFileSelected(event);

    expect(component.selectedFileName).toBe('test.txt');
    expect(mockFileReader.readAsDataURL).toHaveBeenCalledWith(file);

    expect(valueChangeSpy).toHaveBeenCalledWith({
      filename: 'test.txt',
      type: 'text/plain',
      size: 12,
      data: 'data:text/plain;base64,ZmlsZSBjb250ZW50'
    });

    vi.unstubAllGlobals();
  });

  it('should enforce size limits locally', () => {
    component.def.validations = [{ type: 'maxSize', value: 10 }];
    const valueChangeSpy = vi.spyOn(component.valueChange, 'emit');

    const file = new File(['large content'], 'large.txt', { type: 'text/plain' });
    const event = { target: { files: [file] } };

    component.onFileSelected(event);

    expect(component.fileError).toContain('File size must be less than 10 bytes');
    expect(valueChangeSpy).toHaveBeenCalledWith(null);
  });

  it('should enforce type limits locally', () => {
    component.def.validations = [{ type: 'allowedTypes', value: ['image/png'] }];
    const valueChangeSpy = vi.spyOn(component.valueChange, 'emit');

    const file = new File(['text'], 'test.txt', { type: 'text/plain' });
    const event = { target: { files: [file] } };

    component.onFileSelected(event);

    expect(component.fileError).toContain('File type text/plain is not allowed');
    expect(valueChangeSpy).toHaveBeenCalledWith(null);
  });
});
