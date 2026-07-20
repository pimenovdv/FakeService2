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

  it('should notify on answer changes', () => {
    return new Promise<void>((resolve) => {
      service.answerChanges$.subscribe(change => {
        expect(change).toEqual({ componentId: 'q3', value: 'newValue' });
        resolve();
      });
      service.setAnswer('q3', 'newValue');
    });
  });

  it('should update component definitions', () => {
    const dummyScreen: Screen = {
      id: 'screen1',
      header: 'Test Screen',
      content: 'This is a test',
      components: [{ id: 'c1', type: 'text', label: 'C1' }],
      buttons: []
    };
    service.setScreen(dummyScreen);

    service.updateComponentDef('c1', { hidden: true });

    service.componentDefs$.subscribe(defs => {
      expect(defs.find(d => d.id === 'c1')?.hidden).toBe(true);
    });
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


  it('should track validation state', () => {
    service.setValidation('q1', true);
    service.setValidation('q2', false);
    expect(service.isFormValid()).toBe(false);

    service.setValidation('q2', true);
    expect(service.isFormValid()).toBe(true);
  });
  describe('evaluateCondition', () => {
    it('should return false if condition is undefined', () => {
      expect(service.evaluateCondition(undefined)).toBe(false);
    });

    it('should evaluate == operator correctly', () => {
      service.setAnswer('field1', 'yes');
      expect(service.evaluateCondition({ field: 'field1', operator: '==', value: 'yes' })).toBe(true);
      expect(service.evaluateCondition({ field: 'field1', operator: '==', value: 'no' })).toBe(false);
    });

    it('should evaluate != operator correctly', () => {
      service.setAnswer('field1', 'yes');
      expect(service.evaluateCondition({ field: 'field1', operator: '!=', value: 'no' })).toBe(true);
      expect(service.evaluateCondition({ field: 'field1', operator: '!=', value: 'yes' })).toBe(false);
    });

    it('should evaluate > and < operators correctly', () => {
      service.setAnswer('age', 25);
      expect(service.evaluateCondition({ field: 'age', operator: '>', value: 18 })).toBe(true);
      expect(service.evaluateCondition({ field: 'age', operator: '>', value: 30 })).toBe(false);
      expect(service.evaluateCondition({ field: 'age', operator: '<', value: 30 })).toBe(true);
      expect(service.evaluateCondition({ field: 'age', operator: '<', value: 18 })).toBe(false);
    });

    it('should evaluate in operator correctly', () => {
      service.setAnswer('color', 'red');
      expect(service.evaluateCondition({ field: 'color', operator: 'in', value: ['red', 'blue'] })).toBe(true);
      expect(service.evaluateCondition({ field: 'color', operator: 'in', value: ['green', 'yellow'] })).toBe(false);
    });
  });
});
