import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render fallback for unknown component type', () => {
    component.componentDef = {
      id: 'unknown-id',
      type: 'unknown' as any,
      label: 'Unknown Field'
    } as ComponentDef;

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Unsupported component type: unknown (ID: unknown-id)');
  });

  it('should render text input component', () => {
    component.componentDef = {
      id: 'test_text_id',
      type: 'text',
      label: 'Test Text Field'
    } as ComponentDef;

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const textInput = compiled.querySelector('app-text-input');
    expect(textInput).toBeTruthy();
  });
});
