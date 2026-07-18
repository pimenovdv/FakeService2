import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WeekControlComponent } from './week-control.component';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('WeekControlComponent', () => {
  let component: WeekControlComponent;
  let fixture: ComponentFixture<WeekControlComponent>;

  const mockDef: ComponentDef = {
    id: 'testWeek',
    type: 'week',
    label: 'Select Week'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeekControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(WeekControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', '');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display label', async () => {
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    const label = compiled.querySelector('label');
    const input = compiled.querySelector('input');
    expect(label?.textContent).toContain('Select Week');
    expect(input?.type).toBe('week');
  });

  it('should update value on input change', async () => {
    const changeSpy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '2023-W10';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(changeSpy).toHaveBeenCalledWith('2023-W10');
  });
});
