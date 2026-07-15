import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FileControlComponent } from './file-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('FileControlComponent', () => {
  let component: FileControlComponent;
  let fixture: ComponentFixture<FileControlComponent>;
  let stateService: StateService;

  const mockDef: ComponentDef = {
    id: 'test-file',
    type: 'file',
    label: 'Upload File',
    accept: 'image/*',
    multiple: true
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FileControlComponent],
      providers: [StateService]
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

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt'), new File([''], 'file2.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    // In BaseControl, updateValue emits valueChange. Let's spy on the event emitter or check component value.
    expect(component.value.length).toBe(2);
    expect(component.value[0].name).toBe('file1.txt');
    expect(component.value[1].name).toBe('file2.txt');
  });

  it('should handle file selection for single file', () => {
    fixture.componentRef.setInput('def', { ...mockDef, multiple: false });
    fixture.detectChanges();

    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'file1.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(component.value.name).toBe('file1.txt');
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
