import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RatingControlComponent } from './rating-control';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('RatingControlComponent', () => {
  let component: RatingControlComponent;
  let fixture: ComponentFixture<RatingControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RatingControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(RatingControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should update value on click and emit event', async () => {
    const mockDef: ComponentDef = { id: 'rating1', type: 'rating', label: 'Rate Us' };
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
    await fixture.whenStable();

    const spy = vi.spyOn(component.valueChange, 'emit');
    component.setRating(4);

    expect(component.value).toBe(4);
    expect(spy).toHaveBeenCalledWith(4);
  });

  it('should not update value if disabled', async () => {
    const mockDef: ComponentDef = { id: 'rating1', type: 'rating', label: 'Rate Us', disabled: true };
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
    await fixture.whenStable();

    const spy = vi.spyOn(component.valueChange, 'emit');
    component.setRating(3);

    expect(component.value).toBeUndefined();
    expect(spy).not.toHaveBeenCalled();
  });

  it('should update hoverValue on mouseenter and reset on mouseleave', async () => {
    const mockDef: ComponentDef = { id: 'rating1', type: 'rating', label: 'Rate Us' };
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
    await fixture.whenStable();

    component.setHover(5);
    expect(component.hoverValue).toBe(5);

    component.clearHover();
    expect(component.hoverValue).toBe(0);
  });

  it('should validate required rule correctly', async () => {
    const mockDef: ComponentDef = {
      id: 'rating1',
      type: 'rating',
      label: 'Rate Us',
      validations: [{ type: 'required', message: 'Rating is required' }]
    };
    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', undefined);

    component.validate();
    fixture.detectChanges();
    await fixture.whenStable();

    expect(component.isValid).toBe(false);
    expect(component.errors[0]).toBe('Rating is required');

    fixture.componentRef.setInput('value', 2);
    component.validate();
    fixture.detectChanges();
    await fixture.whenStable();

    expect(component.isValid).toBe(true);
    expect(component.errors.length).toBe(0);
  });
});
