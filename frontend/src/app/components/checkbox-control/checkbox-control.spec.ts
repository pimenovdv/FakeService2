import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CheckboxControlComponent } from './checkbox-control';
import { StateService } from '../../services/state';
import { By } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';

describe('CheckboxControlComponent', () => {
  let component: CheckboxControlComponent;
  let fixture: ComponentFixture<CheckboxControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CheckboxControlComponent, FormsModule],
      providers: [StateService]
    }).compileComponents();

    fixture = TestBed.createComponent(CheckboxControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'check1', type: 'checkbox', label: 'Agree to terms' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render label and checkbox', () => {
    component.def = { id: 'check1', type: 'checkbox', label: 'Agree to terms' } as ComponentDef;
    fixture.detectChanges();

    const labelEl = fixture.debugElement.query(By.css('.label-text'));
    expect(labelEl.nativeElement.textContent.trim()).toBe('Agree to terms');

    const inputEl = fixture.debugElement.query(By.css('input[type="checkbox"]'));
    expect(inputEl).toBeTruthy();
  });

  it('should emit value change when toggled', () => {
    component.def = { id: 'check1', type: 'checkbox', label: 'Agree to terms' } as ComponentDef;
    fixture.detectChanges();

    const emitSpy = vi.spyOn(component.valueChange, 'emit');

    component.onValueChange(true);

    expect(emitSpy).toHaveBeenCalledWith(true);
    expect(component.value).toBe(true);
  });

  it('should mark as required if required validation rule is present', () => {
     component.def = {
        id: 'check1',
        type: 'checkbox',
        label: 'Agree to terms',
        validations: [{ type: 'required', message: 'Must check' }]
     } as ComponentDef;
     fixture.detectChanges();

     const requiredMarker = fixture.debugElement.query(By.css('.required-marker'));
     expect(requiredMarker).toBeTruthy();
     expect(requiredMarker.nativeElement.textContent.trim()).toBe('*');
  });
});
