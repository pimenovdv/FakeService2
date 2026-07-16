import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ToggleControlComponent } from './toggle-control';
import { ComponentDef } from '../../models/screen.model';
import { FormsModule } from '@angular/forms';

describe('ToggleControlComponent', () => {
  let component: ToggleControlComponent;
  let fixture: ComponentFixture<ToggleControlComponent>;

  const mockDef: ComponentDef = {
    id: 'toggle1',
    type: 'toggle',
    label: 'Enable Feature'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ToggleControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ToggleControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the label', () => {
    const labelEl = fixture.nativeElement.querySelector('.label-text');
    expect(labelEl.textContent).toContain('Enable Feature');
  });

  it('should bind value correctly', async () => {
    fixture.componentRef.setInput('value', true);
    fixture.detectChanges();
    await fixture.whenStable();

    const inputEl = fixture.nativeElement.querySelector('input[type="checkbox"]');
    expect(inputEl.checked).toBe(true);
  });

  it('should emit value changes', () => {
    let emittedValue: any;
    component.valueChange.subscribe(val => emittedValue = val);

    const inputEl = fixture.nativeElement.querySelector('input[type="checkbox"]');
    inputEl.checked = true;
    inputEl.dispatchEvent(new Event('change'));
    fixture.detectChanges();

    expect(emittedValue).toBe(true);
  });

  it('should handle disabled state', async () => {
    const disabledDef = { ...mockDef, disabled: true };
    fixture.componentRef.setInput('def', disabledDef);
    fixture.detectChanges();
    await fixture.whenStable();

    const inputEl = fixture.nativeElement.querySelector('input[type="checkbox"]');
    expect(inputEl.disabled).toBe(true);
  });

  it('should validate required constraint', () => {
    const reqDef = { ...mockDef, validations: [{ type: 'required' as const }] };
    fixture.componentRef.setInput('def', reqDef);
    component.validate();
    fixture.detectChanges();

    expect(component.isValid).toBe(false);

    fixture.componentRef.setInput('value', true);
    component.validate();
    fixture.detectChanges();

    expect(component.isValid).toBe(true);
  });
});
