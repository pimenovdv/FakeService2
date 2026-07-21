import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ComboboxControlComponent } from './combobox-control';
import { ApiService } from '../../services/api';
import { of, throwError } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('ComboboxControlComponent', () => {
  let component: ComboboxControlComponent;
  let fixture: ComponentFixture<ComboboxControlComponent>;
  let apiServiceMock: any;

  beforeEach(async () => {
    apiServiceMock = {
      dynamicCall: vi.fn().mockReturnValue(of([{ id: 'test', name: 'Test Option' }]))
    };

    await TestBed.configureTestingModule({
      imports: [ComboboxControlComponent],
      providers: [
        { provide: ApiService, useValue: apiServiceMock }
      ]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ComboboxControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'combo1', type: 'combobox', label: 'Combo 1' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should populate static options', () => {
    const staticOptions = [{ id: 'opt1', name: 'Option 1' }, { id: 'opt2', name: 'Option 2' }];
    component.def = {
      id: 'combo_static',
      type: 'combobox',
      label: 'Static Combo',
      options: staticOptions
    } as ComponentDef;

    fixture.detectChanges(); // calls ngOnInit

    expect(component.options).toEqual(staticOptions);
    expect(apiServiceMock.dynamicCall).not.toHaveBeenCalled();
  });

  it('should fetch dynamic options if restMetadata is provided', () => {
    component.def = {
      id: 'combo_dynamic',
      type: 'combobox',
      label: 'Dynamic Combo',
      restMetadata: { endpoint: '/api/options', method: 'GET' }
    } as ComponentDef;

    fixture.detectChanges();

    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({...component.def.restMetadata, params: {}});
    expect(component.options).toEqual([{ id: 'test', name: 'Test Option' }]);
    expect(component.loadingOptions).toBe(false);
  });

  it('should handle dynamic options error', () => {
    apiServiceMock.dynamicCall.mockReturnValue(throwError(() => new Error('API Error')));

    component.def = {
      id: 'combo_dynamic_error',
      type: 'combobox',
      label: 'Dynamic Combo Error',
      restMetadata: { endpoint: '/api/error', method: 'GET' }
    } as ComponentDef;

    fixture.detectChanges();

    expect(apiServiceMock.dynamicCall).toHaveBeenCalled();
    expect(component.optionsError).toBe('Failed to load options');
    expect(component.loadingOptions).toBe(false);
    expect(component.options).toEqual([]);
  });

  it('should reload dynamic options on dependency change', () => {
    const mockData1 = [{ id: 'test1', name: 'Option 1' }];
    const mockData2 = [{ id: 'test2', name: 'Option 2' }];
    apiServiceMock.dynamicCall.mockReturnValueOnce(of(mockData1)).mockReturnValueOnce(of(mockData2));

    // Set up mock answers for dependencies
    const stateService = (component as any).stateService;
    stateService.setAnswer('country', 'US');

    component.def = {
      id: 'combo_dynamic_deps',
      type: 'combobox',
      label: 'Dynamic Combo with Deps',
      restMetadata: { endpoint: '/api/cities', method: 'GET', params: { base: 'value' } },
      dependsOn: ['country']
    } as ComponentDef;

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