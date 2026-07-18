import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DatetimeControlComponent } from './datetime-control.component';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('DatetimeControlComponent', () => {
  let component: DatetimeControlComponent;
  let fixture: ComponentFixture<DatetimeControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatetimeControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(DatetimeControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render datetime-local input', async () => {
    const def: ComponentDef = { id: 'dt1', type: 'datetime', label: 'Test Datetime' };
    fixture.componentRef.setInput('def', def);
    await fixture.whenStable();
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css('input[type="datetime-local"]'));
    expect(input).toBeTruthy();

    const label = fixture.debugElement.query(By.css('label'));
    expect(label.nativeElement.textContent).toContain('Test Datetime');
  });

  it('should update value on input change', async () => {
    const def: ComponentDef = { id: 'dt1', type: 'datetime', label: 'Test Datetime' };
    fixture.componentRef.setInput('def', def);
    fixture.componentRef.setInput('value', '2023-10-10T10:10');
    await fixture.whenStable();
    fixture.detectChanges();

    const spy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.debugElement.query(By.css('input')).nativeElement;

    input.value = '2023-10-11T11:11';
    input.dispatchEvent(new Event('input'));
    await fixture.whenStable();

    expect(spy).toHaveBeenCalledWith('2023-10-11T11:11');
  });

  it('should validate required correctly', async () => {
    const def: ComponentDef = {
      id: 'dt1',
      type: 'datetime',
      label: 'Date Time',
      validations: [{ type: 'required', message: 'Required field' }]
    };
    fixture.componentRef.setInput('def', def);
    fixture.componentRef.setInput('value', '');

    component.validate();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.errors.length).toBeGreaterThan(0);
    expect(component.errors).toContain('Required field');

    fixture.componentRef.setInput('value', '2023-10-10T10:10');
    component.validate();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.errors.length).toBe(0);
  });
});
