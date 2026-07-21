import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DraftsComponent } from './drafts';
import { DraftService, Draft } from '../../services/draft';
import { Router } from '@angular/router';
import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('DraftsComponent', () => {
  let component: DraftsComponent;
  let fixture: ComponentFixture<DraftsComponent>;
  let mockDraftService: any;
  let mockRouter: any;

  const mockDrafts: Draft[] = [
    {
      serviceId: 'service-1',
      screen: { id: 'screen-1', header: 'Screen 1', content: '', components: [], buttons: [] },
      answers: {},
      timestamp: 1000
    },
    {
      serviceId: 'service-2',
      screen: { id: 'screen-2', header: 'Screen 2', content: '', components: [], buttons: [] },
      answers: {},
      timestamp: 2000
    }
  ];

  beforeEach(async () => {
    mockDraftService = {
      getAllDrafts: vi.fn().mockReturnValue(mockDrafts),
      deleteDraft: vi.fn()
    };

    mockRouter = {
      navigate: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [DraftsComponent],
      providers: [
        { provide: DraftService, useValue: mockDraftService },
        { provide: Router, useValue: mockRouter }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DraftsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load drafts on init', () => {
    expect(mockDraftService.getAllDrafts).toHaveBeenCalled();
    expect(component.drafts).toEqual(mockDrafts);
  });

  it('should navigate to player when resume is clicked', () => {
    component.resumeDraft(mockDrafts[0]);
    expect(mockRouter.navigate).toHaveBeenCalledWith(['service-1', '1'], { queryParams: { resume: 'true' } });
  });

  it('should delete draft and reload when delete is clicked', () => {
    component.deleteDraft(mockDrafts[1]);
    expect(mockDraftService.deleteDraft).toHaveBeenCalledWith('service-2');
    expect(mockDraftService.getAllDrafts).toHaveBeenCalledTimes(2); // Once in init, once in delete
  });

  it('should display drafts in template', async () => {
    fixture.detectChanges();
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    const cards = compiled.querySelectorAll('.draft-card');
    expect(cards.length).toBe(2);
    expect(cards[0].textContent).toContain('Screen 1');
    expect(cards[1].textContent).toContain('Screen 2');
  });

  it('should show empty state when no drafts exist', async () => {
    mockDraftService.getAllDrafts.mockReturnValue([]);
    component.loadDrafts();
    fixture.detectChanges();
    await fixture.whenStable();

    const compiled = fixture.nativeElement as HTMLElement;
    const emptyState = compiled.querySelector('.text-gray-500.italic');
    expect(emptyState?.textContent?.trim()).toBe('No saved drafts found.');
    expect(compiled.querySelectorAll('.draft-card').length).toBe(0);
  });
});
