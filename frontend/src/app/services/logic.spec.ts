import { TestBed } from '@angular/core/testing';
import { LogicService } from './logic';
import { StateService } from './state';
import { expect, describe, it, beforeEach, vi } from 'vitest';

describe('LogicService', () => {
  let service: LogicService;
  let stateServiceMock: any;

  beforeEach(() => {
    stateServiceMock = {
      setAnswer: vi.fn(),
      getAnswer: vi.fn(),
      updateComponentDef: vi.fn(),
      isFormValid: vi.fn()
    };

    TestBed.configureTestingModule({
      providers: [
        LogicService,
        { provide: StateService, useValue: stateServiceMock }
      ]
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
