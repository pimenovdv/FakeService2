import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TimeControlComponent } from './time-control';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('TimeControlComponent', () => {
  let component: TimeControlComponent;
  let fixture: ComponentFixture<TimeControlComponent>;

  const mockDef: ComponentDef = {
    id: 'alarmTime',
    type: 'time',
    label: 'Alarm Time',
    validations: [{ type: 'required' }]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TimeControlComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TimeControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render time input with initial value', async () => {
    fixture.componentRef.setInput('value', '12:30');
    fixture.detectChanges();
    await fixture.whenStable();

    const input = fixture.debugElement.query(By.css('input[type="time"]'));
    expect(input).toBeTruthy();
    expect(input.nativeElement.value).toBe('12:30');
  });

  it('should emit value change on input', () => {
    const emitSpy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.debugElement.query(By.css('input[type="time"]'));

    input.nativeElement.value = '14:45';
    input.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(emitSpy).toHaveBeenCalledWith('14:45');
  });

  it('should validate required correctly', () => {
    component.onValueChange('09:00');
    expect(component.isValid).toBe(true);

    component.onValueChange(null);
    expect(component.isValid).toBe(false);
  });
});
