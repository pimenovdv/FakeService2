import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DatepickerControlComponent } from './datepicker-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { ChangeDetectorRef } from '@angular/core';

describe('DatepickerControlComponent', () => {
  let component: DatepickerControlComponent;
  let fixture: ComponentFixture<DatepickerControlComponent>;
  let stateService: StateService;

  const mockDef: ComponentDef = {
    id: 'birthdate',
    type: 'datepicker',
    label: 'Date of Birth',
    validations: [{ type: 'required', message: 'Date is required' }]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatepickerControlComponent],
      providers: [StateService, ChangeDetectorRef]
    }).compileComponents();

    fixture = TestBed.createComponent(DatepickerControlComponent);
    component = fixture.componentInstance;
    stateService = TestBed.inject(StateService);
    component.def = mockDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and input', () => {
    const label = fixture.debugElement.query(By.css('label')).nativeElement;
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    expect(label.textContent.trim()).toBe('Date of Birth');
    expect(input.type).toBe('date');
  });

  it('should update value on input change', () => {
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    input.value = '2023-10-27';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(component.value).toBe('2023-10-27');
  });

  it('should display error if required validation fails on blur', () => {
    component.value = null;
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    input.dispatchEvent(new Event('blur'));
    fixture.detectChanges();

    const errorMsg = fixture.debugElement.query(By.css('.error-text')).nativeElement;
    expect(errorMsg.textContent.trim()).toBe('Date is required');
  });

  it('should not display error if validation passes', () => {
    component.value = '2023-10-27';
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    input.dispatchEvent(new Event('blur'));
    fixture.detectChanges();

    const errorMsg = fixture.debugElement.query(By.css('.error-text'));
    expect(errorMsg).toBeNull();
  });
});
