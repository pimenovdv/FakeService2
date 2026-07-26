import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Player } from './player';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { LogicService } from '../../services/logic';
import { DraftService, Draft } from '../../services/draft';
import { ActivatedRoute } from '@angular/router';
import { BehaviorSubject, Subject, of } from 'rxjs';
import { Screen, ComponentDef, ButtonDef } from '../../models/screen.model';
import { vi, expect, describe, it, beforeEach } from 'vitest';

// Mock html2canvas and jsPDF before tests
vi.mock('html2canvas', () => {
  return {
    default: vi.fn().mockResolvedValue({
      toDataURL: vi.fn().mockReturnValue('data:image/jpeg;base64,mock'),
      height: 100,
      width: 100
    })
  };
});

vi.mock('jspdf', () => {
  return {
    jsPDF: vi.fn().mockImplementation(() => ({
      internal: {
        pageSize: {
          getWidth: vi.fn().mockReturnValue(210)
        }
      },
      addImage: vi.fn(),
      save: vi.fn()
    }))
  };
});

describe('Player', () => {
  let component: Player;
  let fixture: ComponentFixture<Player>;
  let mockApiService: any;
  let mockStateService: any;
  let mockSpeechRecognition: any;
  let mockLogicService: any;
  let mockDraftService: any;
  let mockActivatedRoute: any;
  let currentScreenSubject: BehaviorSubject<Screen | null>;
  let componentDefsSubject: BehaviorSubject<ComponentDef[]>;
  let answerChangesSubject: Subject<{componentId: string, value: any}>;

  beforeEach(async () => {
    localStorage.clear();
    currentScreenSubject = new BehaviorSubject<Screen | null>(null);
    componentDefsSubject = new BehaviorSubject<ComponentDef[]>([]);
    answerChangesSubject = new Subject();

    mockApiService = {
      start: vi.fn().mockReturnValue(of({ id: 'test-screen' } as any)),
      nextStep: vi.fn().mockReturnValue(of({ id: 'next-screen' } as any))
    };

    mockStateService = {
      setScreen: vi.fn().mockImplementation((screen) => currentScreenSubject.next(screen)),
      getScreen: vi.fn().mockReturnValue({ id: 'test-screen' }),
      currentScreen$: currentScreenSubject.asObservable(),
      componentDefs$: componentDefsSubject.asObservable(),
      answerChanges$: answerChangesSubject.asObservable(),
      answers$: of({}),
      evaluateCondition: vi.fn().mockReturnValue(false),
      setSubmitAttempted: vi.fn(),
      isFormValid: vi.fn().mockReturnValue(true),
      getAllAnswers: vi.fn().mockReturnValue({ field1: 'value' }),
      submitAttempted$: of(false),
      setValidation: vi.fn(),
      evaluateCrossValidations: vi.fn().mockReturnValue([]),
      restoreAnswers: vi.fn(),
      clearState: vi.fn()
    };

    mockLogicService = {
      execute: vi.fn()
    };

    mockDraftService = {
      saveDraft: vi.fn(),
      getDraft: vi.fn(),
      deleteDraft: vi.fn()
    };

    mockActivatedRoute = {
      paramMap: of({ get: () => 'test-service' }),
      snapshot: { queryParamMap: { get: vi.fn() } }
    };

    mockSpeechRecognition = function(this: any) {
      this.start = vi.fn();
      this.stop = vi.fn();
    };
    (window as any).SpeechRecognition = mockSpeechRecognition;

    await TestBed.configureTestingModule({
      imports: [Player],
      providers: [
        { provide: ApiService, useValue: mockApiService },
        { provide: StateService, useValue: mockStateService },
        { provide: LogicService, useValue: mockLogicService },
        { provide: DraftService, useValue: mockDraftService },
        { provide: ActivatedRoute, useValue: mockActivatedRoute }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should show confirmation dialog and abort if cancelled', () => {
    mockStateService.getScreen.mockReturnValue({
      id: 'screen1',
      header: 'Screen 1',
      content: 'Content',
      components: [],
      buttons: [{ id: 'submit', label: 'Submit', action: 'submit', confirmMessage: 'Are you sure?' }]
    } as Screen);
    mockStateService.isFormValid.mockReturnValue(true);
    mockStateService.getAllAnswers.mockReturnValue({});

    const confirmSpy = vi.spyOn(window, 'confirm').mockImplementation(() => false);

    component.onButtonClick({ id: 'submit', label: 'Submit', action: 'submit', confirmMessage: 'Are you sure?' } as ButtonDef);

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure?');
    expect(mockStateService.setSubmitAttempted).not.toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('should show confirmation dialog and proceed if confirmed', () => {
    mockStateService.getScreen.mockReturnValue({
      id: 'screen1',
      header: 'Screen 1',
      content: 'Content',
      components: [],
      buttons: [{ id: 'submit', label: 'Submit', action: 'submit', confirmMessage: 'Are you sure?' }]
    } as Screen);
    mockStateService.isFormValid.mockReturnValue(true);
    mockStateService.getAllAnswers.mockReturnValue({});
    mockStateService.evaluateCrossValidations.mockReturnValue([]);
    mockApiService.nextStep.mockReturnValue(of({ completed: true }));

    const confirmSpy = vi.spyOn(window, 'confirm').mockImplementation(() => true);

    component['serviceId'] = '123';

    component.onButtonClick({ id: 'submit', label: 'Submit', action: 'submit', confirmMessage: 'Are you sure?' } as ButtonDef);

    expect(confirmSpy).toHaveBeenCalledWith('Are you sure?');
    expect(mockStateService.setSubmitAttempted).toHaveBeenCalled();

    confirmSpy.mockRestore();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should read service_id from route and call start when not resuming', () => {
    expect(mockApiService.start).toHaveBeenCalledWith('test-service');
  });

  it('should resume draft if resume query param is present', () => {
    const mockDraft: Draft = {
      serviceId: 'test-service',
      screen: { id: 'draft-screen', header: 'Draft', content: '', components: [], buttons: [] },
      answers: { field1: 'draft-val' },
      timestamp: 1000
    };
    mockDraftService.getDraft.mockReturnValue(mockDraft);
    mockActivatedRoute.snapshot.queryParamMap.get.mockReturnValue('true');
    mockApiService.start.mockClear();

    component.ngOnInit();

    expect(mockStateService.setScreen).toHaveBeenCalledWith(mockDraft.screen);
    expect(mockStateService.restoreAnswers).toHaveBeenCalledWith(mockDraft.answers);
    expect(mockApiService.start).not.toHaveBeenCalled(); // was called in beforeEach, but shouldn't be called again
  });

  it('should set screen in state service when start is successful', () => {
    expect(mockStateService.setScreen).toHaveBeenCalledWith({ id: 'test-screen' });
    expect(component.loading).toBeFalsy();
    expect(component.error).toBeNull();
  });

  it('should restore answers from localStorage on load', () => {
    localStorage.setItem('autosave_test-service_test-screen', JSON.stringify({ q1: 'savedValue' }));
    mockApiService.start.mockReturnValue(of({ id: 'test-screen' }));

    component.ngOnInit();

    expect(mockStateService.restoreAnswers).toHaveBeenCalledWith({ q1: 'savedValue' });
  });

  it('should save draft and write answers to localStorage on change', () => {
    component.ngOnInit();

    const screen = { id: 'test-screen' };
    mockStateService.getScreen.mockReturnValue(screen);
    mockStateService.getAllAnswers.mockReturnValue({ q1: 'newVal' });

    answerChangesSubject.next({ componentId: 'q1', value: 'newVal' });

    expect(localStorage.getItem('autosave_test-service_test-screen')).toEqual(JSON.stringify({ q1: 'newVal' }));
    expect(mockDraftService.saveDraft).toHaveBeenCalledWith('test-service', screen, { q1: 'newVal' });
  });

  it('should delete draft on completion', () => {
    mockStateService.isFormValid.mockReturnValue(true);
    mockStateService.getScreen.mockReturnValue({ id: 'test-screen' });
    mockApiService.nextStep.mockReturnValue(of({ completed: true }));

    component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);

    expect(mockDraftService.deleteDraft).toHaveBeenCalledWith('test-service');
    expect(mockStateService.clearState).toHaveBeenCalled();
  });

  it('should clear localStorage on successful next step', () => {
    localStorage.setItem('autosave_test-service_test-screen', 'somedata');
    mockStateService.isFormValid.mockReturnValue(true);

    component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);

    expect(localStorage.getItem('autosave_test-service_test-screen')).toBeNull();
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

  describe('logic execution', () => {
    it('should execute onLoad scripts when starting', () => {
      mockApiService.start.mockReturnValue(of({
        id: 'test-screen',
        scripts: [{ trigger: 'onLoad', code: 'console.log("loaded");' }]
      } as any));

      component.ngOnInit();

      expect(mockLogicService.execute).toHaveBeenCalledWith('console.log("loaded");');
    });

    it('should execute onChange scripts on answer change', () => {
      mockStateService.getScreen.mockReturnValue({
        id: 'test-screen',
        scripts: [{ trigger: 'onChange', targetComponentId: 'q1', code: 'console.log("changed");' }]
      });

      component.ngOnInit();

      answerChangesSubject.next({ componentId: 'q1', value: 'newVal' });

      expect(mockLogicService.execute).toHaveBeenCalledWith('console.log("changed");', { componentId: 'q1', value: 'newVal' });
    });
  });

  describe('onButtonClick', () => {
    it('should set submit attempted and show validation error if form is invalid', () => {
      mockStateService.isFormValid.mockReturnValue(false);
      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);
      expect(mockStateService.setSubmitAttempted).toHaveBeenCalledWith(true);
      expect(component.validationError).toBe('Please correct the errors before proceeding.');
      expect(mockApiService.nextStep).not.toHaveBeenCalled();
    });

    it('should call nextStep if form is valid and clear validation error', () => {
      mockStateService.isFormValid.mockReturnValue(true);
      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);
      expect(mockStateService.setSubmitAttempted).toHaveBeenCalledWith(true);
      expect(component.validationError).toBeNull();
      expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'test-screen', { field1: 'value' });
    });

    it('should show validation error if cross-validations fail', () => {
      mockStateService.isFormValid.mockReturnValue(true);
      mockStateService.getScreen.mockReturnValue({
        id: 'test-screen',
        crossValidations: [{ type: 'match', fields: ['p1', 'p2'], message: 'Passwords do not match' }]
      });
      mockStateService.evaluateCrossValidations.mockReturnValue(['Passwords do not match']);

      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);

      expect(mockStateService.setSubmitAttempted).toHaveBeenCalledWith(true);
      expect(component.validationError).toBe('Passwords do not match');
      expect(mockApiService.nextStep).not.toHaveBeenCalled();
    });

    it('should combine standard and cross-validation errors', () => {
      mockStateService.isFormValid.mockReturnValue(false);
      mockStateService.getScreen.mockReturnValue({
        id: 'test-screen',
        crossValidations: [{ type: 'match', fields: ['p1', 'p2'], message: 'Passwords do not match' }]
      });
      mockStateService.evaluateCrossValidations.mockReturnValue(['Passwords do not match']);

      component.onButtonClick({ id: 'btn', label: 'Next', action: 'next_step' } as any);

      expect(component.validationError).toBe('Please correct the errors before proceeding. Passwords do not match');
      expect(mockApiService.nextStep).not.toHaveBeenCalled();
    });

    it('should call exportPdf if action is export_pdf', () => {
      const exportPdfSpy = vi.spyOn(component, 'exportPdf').mockImplementation(() => Promise.resolve());
      component.onButtonClick({ id: 'btn', label: 'Export', action: 'export_pdf' } as any);
      expect(exportPdfSpy).toHaveBeenCalled();
    });
  });

  it('should return correct theme styles from getThemeStyles', () => {
    const theme = {
      primaryColor: '#ff0000',
      backgroundColor: '#f0f0f0',
      textColor: '#333333',
      fontFamily: 'Arial, sans-serif'
    };
    const styles = component.getThemeStyles(theme);
    expect(styles).toEqual({
      'background-color': '#f0f0f0',
      'color': '#333333',
      'font-family': 'Arial, sans-serif',
      '--theme-primary': '#ff0000'
    });
  });

  it('should return empty object from getThemeStyles when theme is not provided', () => {
    const styles = component.getThemeStyles();
    expect(styles).toEqual({});
  });

  describe('Voice Navigation', () => {
    it('should initialize SpeechRecognition if toggleVoiceNav is called and not active', () => {
      const spy = vi.spyOn(window as any, 'SpeechRecognition');
      component.isVoiceNavActive = false;
      component.toggleVoiceNav();
      expect(spy).toHaveBeenCalled();
      expect(component['recognition']).toBeTruthy();
      expect(component['recognition'].start).toHaveBeenCalled();
    });

    it('should stop SpeechRecognition if toggleVoiceNav is called and active', () => {
      component.isVoiceNavActive = true;
      component['recognition'] = new mockSpeechRecognition();
      const stopSpy = vi.spyOn(component['recognition'], 'stop');
      component.toggleVoiceNav();
      expect(stopSpy).toHaveBeenCalled();
      expect(component.isVoiceNavActive).toBe(false);
      expect(component['recognition']).toBeNull();
    });

    it('should handle voice command to trigger button click', () => {
      const btnNext: ButtonDef = { id: 'next', label: 'Next Step', action: 'next_step' };
      const btnCancel: ButtonDef = { id: 'cancel', label: 'Cancel', action: 'cancel' };

      mockStateService.getScreen.mockReturnValue({
        id: 'test-screen',
        buttons: [btnNext, btnCancel]
      } as Screen);

      const clickSpy = vi.spyOn(component, 'onButtonClick').mockImplementation(() => {});

      component['handleVoiceCommand']('go to the next step');

      expect(clickSpy).toHaveBeenCalledWith(btnNext);
      expect(clickSpy).not.toHaveBeenCalledWith(btnCancel);
    });

    it('should handle voice command and not trigger if no match found', () => {
      const btnNext: ButtonDef = { id: 'next', label: 'Next Step', action: 'next_step' };

      mockStateService.getScreen.mockReturnValue({
        id: 'test-screen',
        buttons: [btnNext]
      } as Screen);

      const clickSpy = vi.spyOn(component, 'onButtonClick').mockImplementation(() => {});

      component['handleVoiceCommand']('submit now');

      expect(clickSpy).not.toHaveBeenCalled();
    });
  });
});
