import { TestBed } from '@angular/core/testing';
import { StateService } from './state';
import { Screen } from '../models/screen.model';

describe('StateService', () => {
  let service: StateService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(StateService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should manage screen state', () => {
    const dummyScreen: Screen = {
      id: 'screen1',
      header: 'Test Screen',
      content: 'This is a test',
      components: [],
      buttons: []
    };

    service.setScreen(dummyScreen);
    expect(service.getScreen()).toEqual(dummyScreen);

    service.currentScreen$.subscribe(screen => {
      expect(screen).toEqual(dummyScreen);
    });
  });

  it('should store and retrieve answers', () => {
    service.setAnswer('q1', 'value1');
    service.setAnswer('q2', 42);

    expect(service.getAnswer('q1')).toBe('value1');
    expect(service.getAnswer('q2')).toBe(42);
    expect(service.getAllAnswers()).toEqual({ q1: 'value1', q2: 42 });
  });

  it('should reset answers when setting a new screen', () => {
    const dummyScreen: Screen = {
      id: 'screen2',
      header: 'Next Screen',
      content: 'This is the next test',
      components: [],
      buttons: []
    };

    service.setAnswer('q1', 'value1');
    service.setScreen(dummyScreen);

    expect(service.getAllAnswers()).toEqual({});
  });

  it('should clear state', () => {
    const dummyScreen: Screen = {
      id: 'screen1',
      header: 'Test',
      content: 'Test content',
      components: [],
      buttons: []
    };

    service.setScreen(dummyScreen);
    service.setAnswer('q1', 'test');
    service.clearState();

    expect(service.getScreen()).toBeNull();
    expect(service.getAllAnswers()).toEqual({});
  });

  it('should evaluate conditions correctly', () => {
    service.setAnswer('q1', 'yes');
    service.setAnswer('q2', 42);

    expect(service.evaluateCondition({ componentId: 'q1', value: 'yes' })).toBeTruthy();
    expect(service.evaluateCondition({ componentId: 'q1', value: 'no' })).toBeFalsy();
    expect(service.evaluateCondition({ componentId: 'q2', value: 42 })).toBeTruthy();
    expect(service.evaluateCondition({ componentId: 'q3', value: 'something' })).toBeFalsy();
  });

  it('should emit new answers to answers$', () => {
    return new Promise<void>((resolve) => {
      let emissionCount = 0;
      service.answers$.subscribe(answers => {
        emissionCount++;
        if (emissionCount === 1) {
          // Initial empty state
          expect(answers).toEqual({});
        } else if (emissionCount === 2) {
          expect(answers).toEqual({ q1: 'value1' });
          resolve();
        }
      });

      service.setAnswer('q1', 'value1');
    });
  });
});
