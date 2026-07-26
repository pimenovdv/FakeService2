import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TextareaControlComponent } from './textarea-control';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('TextareaControlComponent', () => {
  let component: TextareaControlComponent;
  let fixture: ComponentFixture<TextareaControlComponent>;
  let mockSpeechRecognition: any;

  const mockDef: ComponentDef = {
    id: 'testTextarea',
    type: 'textarea',
    label: 'Test Textarea',
    placeholder: 'Enter text here',
    validations: [
      { type: 'required', message: 'Field is required' },
      { type: 'minLength', value: 5, message: 'Min length 5' }
    ]
  };

  beforeEach(async () => {
    mockSpeechRecognition = function() {
      return {
        start: vi.fn(),
        stop: vi.fn(),
        onstart: null,
        onresult: null,
        onerror: null,
        onend: null,
      };
    };

    if (typeof window !== 'undefined') {
      (window as any).SpeechRecognition = mockSpeechRecognition;
    }

    await TestBed.configureTestingModule({
      imports: [TextareaControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(TextareaControlComponent);
    component = fixture.componentInstance;
    component.def = mockDef;
    component.value = '';
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display label and placeholder', () => {
    const labelEl = fixture.debugElement.query(By.css('label')).nativeElement;
    const textareaEl = fixture.debugElement.query(By.css('textarea')).nativeElement;

    expect(labelEl.textContent).toContain('Test Textarea');
    expect(textareaEl.placeholder).toBe('Enter text here');
  });

  it('should emit value changes', () => {
    vi.spyOn(component.valueChange, 'emit');

    const textareaEl = fixture.debugElement.query(By.css('textarea')).nativeElement;
    textareaEl.value = 'New value';
    textareaEl.dispatchEvent(new Event('input'));

    expect(component.valueChange.emit).toHaveBeenCalledWith('New value');
  });

  it('should validate correctly', () => {
    vi.spyOn(component.isValidChange, 'emit');

    // Test empty (required fails)
    component.value = '';
    component.validate();
    expect(component.isValid).toBeFalsy();
    expect(component.errors).toContain('Field is required');

    // Test min length
    component.value = '123';
    component.validate();
    expect(component.isValid).toBeFalsy();
    expect(component.errors).toContain('Min length 5');

    // Test valid
    component.value = '12345';
    component.validate();
    expect(component.isValid).toBeTruthy();
    expect(component.errors.length).toBe(0);
  });

  it('should render character count when maxLength is set', () => {
    component.def = {
      ...component.def,
      validations: [
        { type: 'maxLength', value: 20 }
      ]
    };
    component.value = 'test string';
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const charCount = compiled.querySelector('.character-count');

    expect(charCount).toBeTruthy();
    expect(charCount?.textContent?.trim()).toBe('11 / 20');
  });

  it('should not render character count when maxLength is not set', () => {
    component.def = {
      ...component.def,
      validations: []
    };
    component.value = 'test string';
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const charCount = compiled.querySelector('.character-count');

    expect(charCount).toBeNull();
  });

  describe('Dictation (Web Speech API)', () => {
    it('should initialize SpeechRecognition if enableDictation is true', () => {
      const spy = vi.spyOn(window as any, 'SpeechRecognition');
      component.def = { ...component.def, enableDictation: true };
      component.ngOnInit();
      expect(spy).toHaveBeenCalled();
    });

    it('should not initialize SpeechRecognition if enableDictation is false', () => {
      const spy = vi.spyOn(window as any, 'SpeechRecognition');
      spy.mockClear();
      component.def = { ...component.def, enableDictation: false };
      component.ngOnInit();
      expect(spy).not.toHaveBeenCalled();
    });

    it('should toggle dictation on and off', () => {
      component.def = { ...component.def, enableDictation: true };
      component.ngOnInit();

      const recognitionInstance = (component as any)['recognition'];

      component.toggleDictation();
      expect(recognitionInstance.start).toHaveBeenCalled();

      component.isDictating = true; // simulate start
      component.toggleDictation();
      expect(recognitionInstance.stop).toHaveBeenCalled();
    });

    it('should append transcript to current value on result', () => {
      component.def = { ...component.def, enableDictation: true };
      component.ngOnInit();

      const recognitionInstance = (component as any)['recognition'];
      let emittedValue: any;
      component.valueChange.subscribe(val => emittedValue = val);

      component.value = 'Test';

      recognitionInstance.onresult({
        results: [[{ transcript: 'ing 123' }]]
      });

      expect(emittedValue).toBe('Test ing 123');
      expect(component.value).toBe('Test ing 123');
    });

    it('should render dictation button when enableDictation is true', () => {
      component.def = { ...component.def, enableDictation: true };
      fixture.detectChanges();
      const compiled = fixture.nativeElement as HTMLElement;
      const dictationBtn = compiled.querySelector('.dictation-button');
      expect(dictationBtn).toBeTruthy();
    });
  });
});
