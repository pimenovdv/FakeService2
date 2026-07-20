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
      updateComponentDef: vi.fn()
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

  it('should warn about deferred execution', () => {
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {});
    const code = `
      state.setAnswer('q2', 'computed');
    `;
    service.execute(code);
    expect(consoleSpy).toHaveBeenCalledWith('Safe logic execution is deferred. Code not executed:', code);
    consoleSpy.mockRestore();
  });
});
