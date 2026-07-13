import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DatepickerControlComponent } from './datepicker-control';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';
import { FormsModule } from '@angular/forms';

describe('DatepickerControlComponent', () => {
  let component: DatepickerControlComponent;
  let fixture: ComponentFixture<DatepickerControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DatepickerControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(DatepickerControlComponent);
    component = fixture.componentInstance;
    component.def = { id: 'test-date', type: 'datepicker', label: 'Test Date' } as ComponentDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should handle value changes', () => {
    component.onValueChange('2023-10-15');
    expect(component.value).toBe('2023-10-15');
    expect(component.touched).toBe(true);
  });
});
