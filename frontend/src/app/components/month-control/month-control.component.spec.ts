import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MonthControlComponent } from './month-control.component';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('MonthControlComponent', () => {
  let component: MonthControlComponent;
  let fixture: ComponentFixture<MonthControlComponent>;

  const mockDef: ComponentDef = {
    id: 'testMonth',
    type: 'month',
    label: 'Expiration Month'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MonthControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(MonthControlComponent);
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
    expect(label?.textContent).toContain('Expiration Month');
    expect(input?.type).toBe('month');
  });

  it('should update value on input change', async () => {
    const changeSpy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '2023-10';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(changeSpy).toHaveBeenCalledWith('2023-10');
  });
});
