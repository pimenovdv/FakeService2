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
      start: vi.fn().mockReturnValue(of({ id: 'test-screen' } as Screen)),
      nextStep: vi.fn().mockReturnValue(of({ id: 'test-screen-2' } as Screen))
    };

    mockStateService = {
      setScreen: vi.fn().mockImplementation((screen) => currentScreenSubject.next(screen)),
      getScreen: vi.fn().mockReturnValue({ id: 'test-screen' }),
      currentScreen$: currentScreenSubject.asObservable(),
      answers$: of({}),
      evaluateCondition: vi.fn().mockReturnValue(false),
      getAllAnswers: vi.fn().mockReturnValue({ field1: 'value1' }),
      validateScreen: vi.fn().mockReturnValue(true),
      setSubmitAttempted: vi.fn(),
      isFormValid: vi.fn().mockReturnValue(true),
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

  it('should render action buttons', async () => {
    mockApiService.start.mockReturnValue(of({
      id: 'test-screen',
      header: 'Test Header',
      content: 'Test Content',
      components: [],
      buttons: [
        { id: 'btn-next', label: 'Next', action: 'next_step' }
      ]
    } as Screen));

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const buttons = compiled.querySelectorAll('button');
    expect(buttons.length).toBe(1);
    expect(buttons[0].textContent?.trim()).toBe('Next');
  });

  describe('onButtonClick', () => {
    it('should set submit attempted and show validation error if form is invalid', () => {
      mockStateService.isFormValid.mockReturnValue(false);
      mockStateService.validateScreen.mockReturnValue(false);
      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);
      expect(mockStateService.setSubmitAttempted).toHaveBeenCalledWith(true);
      expect(component.validationError).toBe('Please correct the errors before proceeding.');
      expect(mockApiService.nextStep).not.toHaveBeenCalled();
    });

    it('should call nextStep if form is valid and clear validation error', () => {
      mockStateService.isFormValid.mockReturnValue(true);
      mockStateService.validateScreen.mockReturnValue(true);
      component.serviceId = 'test-service';
      // component.currentScreenId is not directly accessible, but onButtonClick is called via template usually.
      // Wait, the new onButtonClick only takes btn, the old took currentScreenId as well. Let's keep the new one.
      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);
      expect(mockStateService.setSubmitAttempted).toHaveBeenCalledWith(true);
      expect(component.validationError).toBeNull();
      expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'test-screen', { field1: 'value1' });
    });

  });
});
