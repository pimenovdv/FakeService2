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
      validateScreen: vi.fn().mockReturnValue(true)
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
    const buttons = compiled.querySelectorAll('.screen-footer button');
    expect(buttons.length).toBe(1);
    expect(buttons[0].textContent?.trim()).toBe('Next');
  });

  it('should call nextStep on action button click', async () => {
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
    const button = compiled.querySelector('.screen-footer button') as HTMLButtonElement;

    button.click();

    expect(mockStateService.getAllAnswers).toHaveBeenCalled();
    expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'test-screen', { field1: 'value1' });
    expect(mockStateService.setScreen).toHaveBeenCalledWith({ id: 'test-screen-2' });
  });

  it('should prevent submission if validation fails', async () => {
    mockApiService.start.mockReturnValue(of({
      id: 'test-screen',
      header: 'Test Header',
      content: 'Test Content',
      components: [],
      buttons: [
        { id: 'btn-next', label: 'Next', action: 'next_step' }
      ]
    } as Screen));

    mockApiService.nextStep.mockClear();
    mockStateService.validateScreen.mockReturnValue(false);
    mockApiService.nextStep.mockClear();

    fixture = TestBed.createComponent(Player);

    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const button = compiled.querySelector('.screen-footer button') as HTMLButtonElement;

    button.click();

    expect(mockApiService.nextStep).not.toHaveBeenCalled();
    expect(component.validationError).toBe('Please fix the validation errors before proceeding.');
  });

  it('should simulate a full user flow', async () => {
    // 1. Initial Start
    const screen1: Screen = {
      id: 'screen-1',
      header: 'Step 1',
      content: 'Enter name',
      components: [
        { id: 'name', type: 'text', label: 'Name', validations: [{ type: 'required' }] }
      ],
      buttons: [
        { id: 'btn-next', label: 'Next', action: 'next_step' }
      ]
    };

    const screen2: Screen = {
      id: 'screen-2',
      header: 'Step 2',
      content: 'Confirm',
      components: [],
      buttons: [
        { id: 'btn-submit', label: 'Submit', action: 'submit' }
      ]
    };

    mockApiService.start.mockReturnValue(of(screen1));
    mockApiService.nextStep.mockReturnValue(of(screen2));
    mockStateService.validateScreen.mockReturnValue(true);

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;

    // Simulate user answering field
    mockStateService.getAllAnswers.mockReturnValue({ name: 'Alice' });

    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    // Verify first screen loaded
    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.screen-header h1')?.textContent).toContain('Step 1');

    // Click next
    const button = compiled.querySelector('.screen-footer button') as HTMLButtonElement;
    button.click();

    // Verify next step called
    expect(mockApiService.nextStep).toHaveBeenCalledWith('test-service', 'screen-1', { name: 'Alice' });

    // Assuming the component updates itself on next step:
    // Actually the mockStateService.setScreen handles it, and we check if the mock was called with screen2
    expect(mockStateService.setScreen).toHaveBeenCalledWith(screen2);
  });
});
