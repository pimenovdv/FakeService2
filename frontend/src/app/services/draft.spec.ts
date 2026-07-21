import { TestBed } from '@angular/core/testing';
import { DraftService } from './draft';
import { Screen } from '../models/screen.model';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

describe('DraftService', () => {
  let service: DraftService;

  const mockScreen: Screen = {
    id: 'test-screen',
    header: 'Test Header',
    content: 'Test Content',
    components: [],
    buttons: []
  };

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DraftService);
    localStorage.clear();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should save and retrieve a draft', () => {
    vi.setSystemTime(new Date('2024-01-01T00:00:00Z'));
    const expectedTime = Date.now();

    service.saveDraft('service-1', mockScreen, { q1: 'ans1' });

    const draft = service.getDraft('service-1');
    expect(draft).toBeTruthy();
    expect(draft?.serviceId).toBe('service-1');
    expect(draft?.screen).toEqual(mockScreen);
    expect(draft?.answers).toEqual({ q1: 'ans1' });
    expect(draft?.timestamp).toBe(expectedTime);
  });

  it('should update an existing draft', () => {
    vi.setSystemTime(new Date('2024-01-01T00:00:00Z'));
    service.saveDraft('service-1', mockScreen, { q1: 'ans1' });

    vi.setSystemTime(new Date('2024-01-02T00:00:00Z'));
    const expectedTime2 = Date.now();
    service.saveDraft('service-1', mockScreen, { q1: 'ans2' });

    const draft = service.getDraft('service-1');
    expect(draft?.answers).toEqual({ q1: 'ans2' });
    expect(draft?.timestamp).toBe(expectedTime2);

    const allDrafts = service.getAllDrafts();
    expect(allDrafts.length).toBe(1);
  });

  it('should get all drafts sorted by timestamp descending', () => {
    vi.setSystemTime(new Date('2024-01-01T00:00:00Z'));
    service.saveDraft('service-1', mockScreen, { q1: '1' });

    vi.setSystemTime(new Date('2024-01-03T00:00:00Z'));
    service.saveDraft('service-3', mockScreen, { q1: '3' });

    vi.setSystemTime(new Date('2024-01-02T00:00:00Z'));
    service.saveDraft('service-2', mockScreen, { q1: '2' });

    const allDrafts = service.getAllDrafts();
    expect(allDrafts.length).toBe(3);
    expect(allDrafts[0].serviceId).toBe('service-3');
    expect(allDrafts[1].serviceId).toBe('service-2');
    expect(allDrafts[2].serviceId).toBe('service-1');
  });

  it('should delete a draft', () => {
    service.saveDraft('service-1', mockScreen, { q1: '1' });
    service.saveDraft('service-2', mockScreen, { q2: '2' });

    service.deleteDraft('service-1');

    expect(service.getDraft('service-1')).toBeNull();
    const allDrafts = service.getAllDrafts();
    expect(allDrafts.length).toBe(1);
    expect(allDrafts[0].serviceId).toBe('service-2');
  });

  it('should return empty array if no drafts exist', () => {
    expect(service.getAllDrafts()).toEqual([]);
  });

  it('should return null if draft does not exist', () => {
    expect(service.getDraft('non-existent')).toBeNull();
  });
});
