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

  describe('evaluateCondition', () => {
    it('should return true if no condition is provided', () => {
      expect(service.evaluateCondition(undefined)).toBe(true);
    });

    it('should evaluate hasValue correctly', () => {
      service.setAnswer('field1', 'some value');
      expect(service.evaluateCondition({ field: 'field1', hasValue: true })).toBe(true);
      expect(service.evaluateCondition({ field: 'field1', hasValue: false })).toBe(false);

      expect(service.evaluateCondition({ field: 'field2', hasValue: true })).toBe(false);
      expect(service.evaluateCondition({ field: 'field2', hasValue: false })).toBe(true);

      service.setAnswer('field3', '');
      expect(service.evaluateCondition({ field: 'field3', hasValue: true })).toBe(false);
      expect(service.evaluateCondition({ field: 'field3', hasValue: false })).toBe(true);
    });

    it('should evaluate equals correctly', () => {
      service.setAnswer('field1', 'exact match');
      expect(service.evaluateCondition({ field: 'field1', equals: 'exact match' })).toBe(true);
      expect(service.evaluateCondition({ field: 'field1', equals: 'wrong match' })).toBe(false);

      service.setAnswer('numField', 42);
      expect(service.evaluateCondition({ field: 'numField', equals: 42 })).toBe(true);
      expect(service.evaluateCondition({ field: 'numField', equals: '42' })).toBe(false); // strict equality
    });

    it('should evaluate both hasValue and equals if both provided', () => {
      service.setAnswer('field1', 'test');
      expect(service.evaluateCondition({ field: 'field1', hasValue: true, equals: 'test' })).toBe(true);
      expect(service.evaluateCondition({ field: 'field1', hasValue: true, equals: 'wrong' })).toBe(false);
    });
  });
});
