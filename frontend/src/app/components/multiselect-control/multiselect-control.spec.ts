import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MultiselectControlComponent } from './multiselect-control';
import { ApiService } from '../../services/api';
import { of, throwError } from 'rxjs';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('MultiselectControlComponent', () => {
  let component: MultiselectControlComponent;
  let fixture: ComponentFixture<MultiselectControlComponent>;
  let apiServiceMock: any;

  beforeEach(async () => {
    apiServiceMock = {
      dynamicCall: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [MultiselectControlComponent, FormsModule],
      providers: [
        { provide: ApiService, useValue: apiServiceMock }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(MultiselectControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    const def: ComponentDef = { id: 'test', type: 'multiselect', label: 'Test Multiselect' };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load static options', () => {
    const def: ComponentDef = {
      id: 'test',
      type: 'multiselect',
      label: 'Test',
      options: ['Option 1', 'Option 2']
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();
    expect(component.options.length).toBe(2);
    expect(component.options[0]).toBe('Option 1');
  });

  it('should load dynamic options successfully', () => {
    const def: ComponentDef = {
      id: 'test',
      type: 'multiselect',
      label: 'Test',
      restMetadata: { endpoint: '/test', method: 'GET' }
    };
    const mockData = [{ id: 1, name: 'Dyn 1' }, { id: 2, name: 'Dyn 2' }];
    apiServiceMock.dynamicCall.mockReturnValue(of(mockData));

    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({...def.restMetadata, params: {}});
    expect(component.options).toEqual(mockData);
    expect(component.loadingOptions).toBe(false);
  });

  it('should handle dynamic options error', () => {
    const def: ComponentDef = {
      id: 'test',
      type: 'multiselect',
      label: 'Test',
      restMetadata: { endpoint: '/test', method: 'GET' }
    };
    apiServiceMock.dynamicCall.mockReturnValue(throwError(() => new Error('API Error')));

    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    expect(component.optionsError).toBe('Failed to load options');
    expect(component.loadingOptions).toBe(false);
  });

  it('should validate required correctly', () => {
    const def: ComponentDef = {
      id: 'test',
      type: 'multiselect',
      label: 'Test',
      options: ['1', '2'],
      validations: [{ type: 'required', message: 'Required field' }]
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    component.validate();
    expect(component.isValid).toBe(false);
    expect(component.errors).toContain('Required field');

    fixture.componentRef.setInput('value', ['1']);
    component.validate();
    expect(component.isValid).toBe(true);
    expect(component.errors.length).toBe(0);
  });

  it('should reload dynamic options on dependency change', () => {
    const mockData1 = [{ id: 'test1', name: 'Option 1' }];
    const mockData2 = [{ id: 'test2', name: 'Option 2' }];
    apiServiceMock.dynamicCall.mockReturnValueOnce(of(mockData1)).mockReturnValueOnce(of(mockData2));

    const stateService = (component as any).stateService;
    stateService.setAnswer('country', 'US');

    const def: ComponentDef = {
      id: 'multi_dynamic_deps',
      type: 'multiselect',
      label: 'Dynamic Multi with Deps',
      restMetadata: { endpoint: '/api/cities', method: 'GET', params: { base: 'value' } },
      dependsOn: ['country']
    };

    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    // Initial load checks if API is called with mapped dependency answers
    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({
      endpoint: '/api/cities',
      method: 'GET',
      params: { base: 'value', country: 'US' }
    });
    expect(component.options).toEqual(mockData1);

    // Simulate dependency change
    stateService.setAnswer('country', 'CA');

    // Second API call should occur with new dependency values
    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({
      endpoint: '/api/cities',
      method: 'GET',
      params: { base: 'value', country: 'CA' }
    });
    expect(component.options).toEqual(mockData2);
  });
});
