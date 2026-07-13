import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BaseControl } from './base-control';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach, vi } from 'vitest';

@Component({
  template: ''
})
class TestControl extends BaseControl {}

describe('BaseControl', () => {
  let component: TestControl;
  let fixture: ComponentFixture<TestControl>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestControl]
    }).compileComponents();

    fixture = TestBed.createComponent(TestControl);
    component = fixture.componentInstance;
    component.def = { id: 'test_id', type: 'text', label: 'Test Label' } as ComponentDef;
  });

  it('should initialize empty errors and touched false', () => {
    expect(component.errors).toEqual([]);
    expect(component.touched).toBe(false);
    expect(component.isValid).toBe(true);
  });

  it('should emit value change and trigger validation', () => {
    const valueChangeSpy = vi.spyOn(component.valueChange, 'emit');
    const validateSpy = vi.spyOn(component, 'validate');

    component.onValueChange('test value');

    expect(component.value).toBe('test value');
    expect(component.touched).toBe(true);
    expect(valueChangeSpy).toHaveBeenCalledWith('test value');
    expect(validateSpy).toHaveBeenCalled();
  });

  describe('Validations', () => {
    it('should validate required', () => {
      component.def = {
        id: 'test', type: 'text', label: 'Test',
        validations: [{ type: 'required', message: 'Required field' }]
      } as ComponentDef;

      component.onValueChange('');
      expect(component.errors).toContain('Required field');
      expect(component.isValid).toBe(false);

      component.onValueChange('value');
      expect(component.errors.length).toBe(0);
      expect(component.isValid).toBe(true);
    });

    it('should validate regex', () => {
      component.def = {
        id: 'test', type: 'text', label: 'Test',
        validations: [{ type: 'regex', value: '^\\d+$', message: 'Must be digits' }]
      } as ComponentDef;

      component.onValueChange('abc');
      expect(component.errors).toContain('Must be digits');

      component.onValueChange('123');
      expect(component.errors.length).toBe(0);
    });

    it('should validate min and max', () => {
      component.def = {
        id: 'test', type: 'text', label: 'Test',
        validations: [
          { type: 'min', value: 5, message: 'Min 5' },
          { type: 'max', value: 10, message: 'Max 10' }
        ]
      } as ComponentDef;

      component.onValueChange(3);
      expect(component.errors).toContain('Min 5');

      component.onValueChange(12);
      expect(component.errors).toContain('Max 10');

      component.onValueChange(7);
      expect(component.errors.length).toBe(0);
    });

    it('should validate minLength and maxLength', () => {
      component.def = {
        id: 'test', type: 'text', label: 'Test',
        validations: [
          { type: 'minLength', value: 3, message: 'MinLen 3' },
          { type: 'maxLength', value: 5, message: 'MaxLen 5' }
        ]
      } as ComponentDef;

      component.onValueChange('ab');
      expect(component.errors).toContain('MinLen 3');

      component.onValueChange('abcdef');
      expect(component.errors).toContain('MaxLen 5');

      component.onValueChange('abcd');
      expect(component.errors.length).toBe(0);
    });
  });
});
