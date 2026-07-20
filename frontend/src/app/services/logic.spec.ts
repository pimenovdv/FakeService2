import { TestBed } from '@angular/core/testing';
import { LogicService } from './logic';
import { StateService } from './state';
import { ApiService } from './api';
import { of, throwError } from 'rxjs';
import { expect, describe, it, beforeEach, vi } from 'vitest';

describe('LogicService', () => {
  let service: LogicService;
  let stateServiceMock: any;
  let apiServiceMock: any;

  beforeEach(() => {
    stateServiceMock = {
      setAnswer: vi.fn(),
      getAnswer: vi.fn(),
      updateComponentDef: vi.fn(),
      isFormValid: vi.fn(),
      getComponentDef: vi.fn(),
      getAllAnswers: vi.fn(),
      evaluateCondition: vi.fn(),
    };

    apiServiceMock = {
      dynamicCall: vi.fn()
    };

    TestBed.configureTestingModule({
      providers: [
        LogicService,
        { provide: StateService, useValue: stateServiceMock },
        { provide: ApiService, useValue: apiServiceMock }
      ],
    });
    service = TestBed.inject(LogicService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should execute logic and interact with stateService', () => {
    stateServiceMock.getAnswer.mockReturnValue('initial');
    stateServiceMock.isFormValid.mockReturnValue(true);

    const code = `
      var val = state.getAnswer('q1');
      if (val === 'initial') {
        state.setAnswer('q2', 'computed');
        state.updateComponentDef('q3', { hidden: true });
      }
      var valid = state.isFormValid();
      if (valid) {
        state.setAnswer('q4', 'valid');
      }
    `;
    service.execute(code);

    expect(stateServiceMock.getAnswer).toHaveBeenCalledWith('q1');
    expect(stateServiceMock.setAnswer).toHaveBeenCalledWith('q2', 'computed');
    expect(stateServiceMock.updateComponentDef).toHaveBeenCalledWith('q3', { hidden: true });
    expect(stateServiceMock.isFormValid).toHaveBeenCalled();
    expect(stateServiceMock.setAnswer).toHaveBeenCalledWith('q4', 'valid');
  });

  it('should expose advanced state methods (getComponentDef, getAllAnswers, evaluateCondition)', () => {
    stateServiceMock.getComponentDef.mockReturnValue({ id: 'q1', type: 'text' });
    stateServiceMock.getAllAnswers.mockReturnValue({ q1: 'test' });
    stateServiceMock.evaluateCondition.mockReturnValue(true);

    const code = `
      var def = state.getComponentDef('q1');
      var all = state.getAllAnswers();
      var isMatch = state.evaluateCondition({ field: 'q1', operator: '==', value: 'test' });
      if (def.type === 'text' && all.q1 === 'test' && isMatch) {
        state.setAnswer('result', 'success');
      }
    `;
    service.execute(code);

    expect(stateServiceMock.getComponentDef).toHaveBeenCalledWith('q1');
    expect(stateServiceMock.getAllAnswers).toHaveBeenCalled();
    expect(stateServiceMock.evaluateCondition).toHaveBeenCalledWith({
      field: 'q1',
      operator: '==',
      value: 'test',
    });
    expect(stateServiceMock.setAnswer).toHaveBeenCalledWith('result', 'success');
  });

  it('should execute apiCall asynchronously', async () => {
    apiServiceMock.dynamicCall.mockReturnValue(of({ result: 'api_success' }));

    const code = `
      var res = apiCall('/api/test', 'GET', { filter: 'test' });
      if (res && res.result === 'api_success') {
        state.setAnswer('async_result', 'success');
      }
    `;
    service.execute(code);

    // Wait for the async macro-task (setTimeout inside runInterpreter and rxjs macro tasks if any)
    await new Promise(r => setTimeout(r, 50));

    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({
      endpoint: '/api/test',
      method: 'GET',
      params: { filter: 'test' }
    });
    expect(stateServiceMock.setAnswer).toHaveBeenCalledWith('async_result', 'success');
  });

  it('should handle apiCall errors asynchronously', async () => {
    apiServiceMock.dynamicCall.mockReturnValue(throwError(() => new Error('API Error')));
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    const code = `
      var res = apiCall('/api/error', 'POST', {});
      if (res && res.error) {
        state.setAnswer('async_error', 'caught');
      }
    `;
    service.execute(code);

    await new Promise(r => setTimeout(r, 50));

    expect(apiServiceMock.dynamicCall).toHaveBeenCalledWith({
      endpoint: '/api/error',
      method: 'POST',
      params: {}
    });
    expect(stateServiceMock.setAnswer).toHaveBeenCalledWith('async_error', 'caught');
    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });

  it('should gracefully handle execution errors', () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
    const code = `
      syntax error;
    `;
    service.execute(code);
    expect(consoleSpy).toHaveBeenCalled();
    consoleSpy.mockRestore();
  });
});
