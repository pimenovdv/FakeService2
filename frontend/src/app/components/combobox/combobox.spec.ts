import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ComboBoxComponent } from './combobox';
import { ApiService } from '../../services/api';
import { of, throwError } from 'rxjs';
import { ComponentDef } from '../../models/screen.model';
import { vi } from 'vitest';

describe('ComboBoxComponent', () => {
  let component: ComboBoxComponent;
  let fixture: ComponentFixture<ComboBoxComponent>;
  let apiServiceMock: any;

  beforeEach(async () => {
    apiServiceMock = {
      dynamicCall: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [ComboBoxComponent],
      providers: [
        { provide: ApiService, useValue: apiServiceMock }
      ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComboBoxComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'combo1', type: 'combobox', label: 'Test' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should load static options', () => {
    const options = [{ value: '1', label: 'One' }, { value: '2', label: 'Two' }];
    component.def = {
      id: 'combo1', type: 'combobox', label: 'Test',
      options: options
    } as ComponentDef;

    fixture.detectChanges(); // calls ngOnInit

    expect(component.options).toEqual(options);
    expect(apiServiceMock.dynamicCall).not.toHaveBeenCalled();
  });

  it('should load dynamic options from array response', () => {
    const options = [{ value: 'a', label: 'A' }];
    apiServiceMock.dynamicCall.mockReturnValue(of(options));

    component.def = {
      id: 'combo1', type: 'combobox', label: 'Test',
      restMetadata: { endpoint: '/api/opts', method: 'GET' }
    } as ComponentDef;

    fixture.detectChanges();

    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({ endpoint: '/api/opts', method: 'GET' });
    expect(component.options).toEqual(options);
    expect(component.loading).toBe(false);
  });

  it('should load dynamic options from object response with options array', () => {
    const options = [{ value: 'a', label: 'A' }];
    apiServiceMock.dynamicCall.mockReturnValue(of({ options }));

    component.def = {
      id: 'combo1', type: 'combobox', label: 'Test',
      restMetadata: { endpoint: '/api/opts', method: 'GET' }
    } as ComponentDef;

    fixture.detectChanges();

    expect(component.options).toEqual(options);
  });

  it('should handle error fetching dynamic options', () => {
    apiServiceMock.dynamicCall.mockReturnValue(throwError(() => new Error('Network error')));

    component.def = {
      id: 'combo1', type: 'combobox', label: 'Test',
      restMetadata: { endpoint: '/api/opts', method: 'GET' }
    } as ComponentDef;

    fixture.detectChanges();

    expect(component.errorFetching).toBe(true);
    expect(component.loading).toBe(false);
    expect(component.options).toEqual([]);
  });
});
