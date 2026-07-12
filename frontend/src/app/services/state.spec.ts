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

  it('should evaluate dependencies correctly', () => {
    const compNoDeps = { id: 'c1', type: 'text', label: 'C1' } as any;
    const compWithDeps = { id: 'c2', type: 'text', label: 'C2', dependsOn: ['c1'] } as any;

    expect(service.evaluateDependencies(compNoDeps)).toBeTruthy();
    expect(service.evaluateDependencies(compWithDeps)).toBeFalsy();

    service.setAnswer('c1', 'value');
    expect(service.evaluateDependencies(compWithDeps)).toBeTruthy();
  });

  it('should compute isScreenValid correctly', () => {
    const dummyScreen: Screen = {
      id: 'screen1',
      header: 'Test',
      content: 'Test content',
      components: [
        { id: 'c1', type: 'text', label: 'C1' },
        { id: 'c2', type: 'text', label: 'C2', dependsOn: ['c1'] }
      ] as any[],
      buttons: []
    };
    service.setScreen(dummyScreen);

    // Initial state: c1 valid (undefined validation state defaults to true), c2 hidden (valid)
    expect(service.isScreenValid()).toBeTruthy();

    service.setValidationState('c1', false);
    expect(service.isScreenValid()).toBeFalsy();

    service.setValidationState('c1', true);
    expect(service.isScreenValid()).toBeTruthy();

    service.setAnswer('c1', 'value');
    // Now c2 is visible. If its validation state is undefined, it defaults to true
    expect(service.isScreenValid()).toBeTruthy();

    service.setValidationState('c2', false);
    expect(service.isScreenValid()).toBeFalsy();
  });
});
