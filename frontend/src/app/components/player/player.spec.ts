import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Player } from './player';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { Screen } from '../../models/screen.model';
import { vi, expect, describe, it, beforeEach } from 'vitest';

describe('Player', () => {
  let component: Player;
  let fixture: ComponentFixture<Player>;
  let mockApiService: any;
  let mockStateService: any;
  let mockActivatedRoute: any;
  let currentScreenSubject: BehaviorSubject<Screen | null>;

  beforeEach(async () => {
    currentScreenSubject = new BehaviorSubject<Screen | null>(null);

    mockApiService = {
      start: vi.fn().mockReturnValue(of({ id: 'test-screen' } as any)),
      nextStep: vi.fn().mockReturnValue(of({ id: 'next-screen' } as any))
    };

    mockStateService = {
      setScreen: vi.fn().mockImplementation((screen) => currentScreenSubject.next(screen)),
      getScreen: vi.fn().mockReturnValue({ id: 'test-screen' }),
      currentScreen$: currentScreenSubject.asObservable(),
      answers$: of({}),
      evaluateCondition: vi.fn().mockReturnValue(false),
      getAnswer: vi.fn().mockReturnValue(null),
      setAnswer: vi.fn(),
      setSubmitAttempted: vi.fn(),
      isFormValid: vi.fn().mockReturnValue(true),
      getAllAnswers: vi.fn().mockReturnValue({ field1: 'value' }),
      submitAttempted$: of(false),
      setValidation: vi.fn()
    };

    mockActivatedRoute = {
      paramMap: of({ get: () => 'test-service' })
    };

    await TestBed.configureTestingModule({
      imports: [Player],
      providers: [
        { provide: ApiService, useValue: mockApiService },
        { provide: StateService, useValue: mockStateService },
        { provide: ActivatedRoute, useValue: mockActivatedRoute }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should read service_id from route and call start', () => {
    expect(mockApiService.start).toHaveBeenCalledWith('test-service');
  });

  it('should set screen in state service when start is successful', () => {
    expect(mockStateService.setScreen).toHaveBeenCalledWith({ id: 'test-screen' });
    expect(component.loading).toBeFalsy();
    expect(component.error).toBeNull();
  });

  it('should render screen header and content', async () => {
    mockApiService.start.mockReturnValue(of({
      id: 'test-screen',
      header: 'Test Header',
      content: 'Test Content',
      components: [
        { id: 'field1', type: 'text', label: 'Field 1' }
      ]
    } as Screen));

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;

    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.screen-header h1')?.textContent).toContain('Test Header');
    expect(compiled.querySelector('.screen-content p')?.textContent).toContain('Test Content');
  });

  it('should prevent nextStep if validation fails', () => {
    component.dynamicFields = {
      forEach: (cb: any) => cb({ validate: () => false })
    } as any;

    component.onAction({ id: 'btn', label: 'Next', action: 'next_step' } as any);

    expect(component.validationError).toBe('Please correct the errors before proceeding.');
  });

  it('should call apiService.nextStep and set next screen on success', () => {
    mockStateService.getAllAnswers = vi.fn().mockReturnValue({ field1: 'value' });
    mockStateService.getScreen = vi.fn().mockReturnValue({ id: 'current-screen' });
    mockApiService.nextStep = vi.fn().mockReturnValue(of({ next_screen: { id: 'next-screen' } }));

    component.serviceId = 'test-service';
    component.dynamicFields = {
      forEach: (cb: any) => cb({ validate: () => true })
    } as any;

    component.onAction({ id: 'btn', label: 'Next', action: 'next_step' } as any);

    expect(component.validationError).toBeNull();
    expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'current-screen', { field1: 'value' });
    expect(mockStateService.setScreen).toHaveBeenCalledWith({ id: 'next-screen' });
  });

  it('should call apiService.nextStep and set completed on success', () => {
    mockStateService.getAllAnswers = vi.fn().mockReturnValue({ field1: 'value' });
    mockStateService.getScreen = vi.fn().mockReturnValue({ id: 'current-screen' });
    mockApiService.nextStep = vi.fn().mockReturnValue(of({ completed: true }));

    component.serviceId = 'test-service';
    component.dynamicFields = {
      forEach: (cb: any) => cb({ validate: () => true })
    } as any;

    component.onAction({ id: 'btn', label: 'Next', action: 'next_step' } as any);

    expect(component.validationError).toBeNull();
    expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'current-screen', { field1: 'value' });
    expect(component.completed).toBeTruthy();
  });
});