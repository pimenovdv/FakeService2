import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { BehaviorSubject } from 'rxjs';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { vi, expect, describe, it, beforeEach } from 'vitest';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;
  let mockStateService: any;
  let answersSubject: BehaviorSubject<Record<string, any>>;

  beforeEach(async () => {
    answersSubject = new BehaviorSubject<Record<string, any>>({});
    mockStateService = {
      answers$: answersSubject.asObservable(),
      evaluateCondition: vi.fn().mockReturnValue(false),
      getAllAnswers: vi.fn().mockReturnValue({}),
      setAnswer: vi.fn(),
      setValidation: vi.fn(),
      submitAttempted$: new BehaviorSubject(false).asObservable()
    };

    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent, NoopAnimationsModule],
      providers: [
        { provide: StateService, useValue: mockStateService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.componentDef = { id: 'test1', type: 'text', label: 'Test' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render text input component', () => {
    component.componentDef = { id: 'field1', type: 'text', label: 'Text Field' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-text-input')).toBeTruthy();
  });

  it('should render radio component', () => {
    component.componentDef = { id: 'fieldRadio', type: 'radio', label: 'Radio Field' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-radio-control')).toBeTruthy();
  });

  it('should render fallback for unknown component type', () => {
    component.componentDef = { id: 'field2', type: 'unknown' as any, label: 'Unknown Field' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.fallback-field')?.textContent).toContain('Unsupported component type: unknown');
  });

  it('should reactively evaluate showIf conditions and update hidden state', () => {
    component.componentDef = {
      id: 'field3', type: 'text', label: 'Dependent',
      showIf: { field: 'otherField', operator: '==', value: 'show' }
    } as ComponentDef;

    mockStateService.evaluateCondition.mockReturnValue(true);
    fixture.detectChanges(); // initial evaluation via ngOnInit

    expect(component.isHidden).toBe(false);

    mockStateService.evaluateCondition.mockReturnValue(false);
    answersSubject.next({ otherField: 'hide' }); // trigger evaluation
    fixture.detectChanges();

    expect(component.isHidden).toBe(true);
  });

  it('should reactively evaluate disableIf conditions and update state', () => {
    component.componentDef = {
      id: 'field4', type: 'text', label: 'Dependent',
      disableIf: { field: 'otherField', operator: '==', value: 'disable' }
    } as ComponentDef;

    mockStateService.evaluateCondition.mockReturnValue(false);
    fixture.detectChanges();

    expect(component.isDisabled).toBe(false);

    mockStateService.evaluateCondition.mockReturnValue(true);
    answersSubject.next({ otherField: 'disable' });
    fixture.detectChanges();

    expect(component.isDisabled).toBe(true);
    expect(component.componentDef.disabled).toBe(true); // check if passed down
  });

  it('should set title attribute when tooltip is provided', () => {
    component.componentDef = { id: 'field5', type: 'text', label: 'Tooltip Field', tooltip: 'This is a tooltip' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.dynamic-field-container');
    expect(container?.getAttribute('title')).toBe('This is a tooltip');
  });

  it('should render help text when provided', () => {
    component.componentDef = { id: 'field6', type: 'text', label: 'Help Text Field', helpText: 'This is helpful text' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const helpTextDiv = compiled.querySelector('.help-text');
    expect(helpTextDiv).toBeTruthy();
    expect(helpTextDiv?.textContent).toContain('This is helpful text');
  });

  it('should render accordion and toggle its state', () => {
    component.componentDef = {
      id: 'accordion1',
      type: 'accordion',
      label: 'My Accordion',
      components: [
        { id: 'child1', type: 'text', label: 'Child Text' } as ComponentDef
      ]
    } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    // Accordion should be rendered
    const accordionDiv = compiled.querySelector('.accordion');
    expect(accordionDiv).toBeTruthy();

    // Default state: collapsed, so child component shouldn't be rendered yet
    expect(component.isAccordionExpanded).toBe(false);
    expect(compiled.querySelector('app-text-input')).toBeFalsy();

    // Click header to toggle
    const headerButton = compiled.querySelector('.accordion-header') as HTMLButtonElement;
    headerButton.click();
    fixture.detectChanges();

    // After toggle: expanded, child component should be rendered
    expect(component.isAccordionExpanded).toBe(true);
    expect(compiled.querySelector('app-dynamic-field')).toBeTruthy();
  });

  it('should render tabs and switch content', () => {
    component.componentDef = {
      id: 'tabs1',
      type: 'tabs',
      label: 'My Tabs',
      components: [
        { id: 'tab1', type: 'text', label: 'Tab 1' } as ComponentDef,
        { id: 'tab2', type: 'radio', label: 'Tab 2' } as ComponentDef
      ]
    } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;

    // Tabs container should be rendered
    const tabsContainer = compiled.querySelector('.tabs-container');
    expect(tabsContainer).toBeTruthy();

    // Tab buttons should be rendered
    const tabButtons = compiled.querySelectorAll('.tabs-header button');
    expect(tabButtons.length).toBe(2);
    expect(tabButtons[0].textContent?.trim()).toBe('Tab 1');
    expect(tabButtons[1].textContent?.trim()).toBe('Tab 2');

    // Default state: first tab active, rendering app-text-input
    expect(component.activeTabIndex).toBe(0);
    expect(compiled.querySelector('app-text-input')).toBeTruthy();
    expect(compiled.querySelector('app-radio-control')).toBeFalsy();

    // Click second tab to switch
    (tabButtons[1] as HTMLButtonElement).click();
    fixture.detectChanges();

    // After switch: second tab active, rendering app-radio-control
    expect(component.activeTabIndex).toBe(1);
    expect(compiled.querySelector('app-text-input')).toBeFalsy();
    expect(compiled.querySelector('app-radio-control')).toBeTruthy();
  });

  it('should render carousel with image options', () => {
    component.componentDef = {
      id: 'carousel1',
      type: 'carousel',
      label: 'My Carousel',
      options: [
        { value: 'img1.png', label: 'Image 1' },
        { value: 'img2.png', label: 'Image 2' }
      ]
    } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const carouselContainer = compiled.querySelector('.carousel-container');
    expect(carouselContainer).toBeTruthy();

    const images = compiled.querySelectorAll('img');
    expect(images.length).toBe(2);
    expect(images[0].getAttribute('src')).toBe('img1.png');
    expect(images[0].getAttribute('alt')).toBe('Image 1');
  });

  it('should render carousel with nested dynamic-field components', () => {
    component.componentDef = {
      id: 'carousel2',
      type: 'carousel',
      label: 'Components Carousel',
      components: [
        { id: 'childText', type: 'text', label: 'Text Field' } as ComponentDef,
        { id: 'childRadio', type: 'radio', label: 'Radio Field' } as ComponentDef
      ]
    } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const dynamicFields = compiled.querySelectorAll('app-dynamic-field');

    // There are 2 nested dynamic-fields rendered inside the carousel
    expect(dynamicFields.length).toBe(2);
  });

  it('should call scrollCarousel when next/prev buttons are clicked', () => {
    component.componentDef = {
      id: 'carousel3',
      type: 'carousel',
      label: 'Scrollable Carousel',
      options: [{ value: 'img1.png' }, { value: 'img2.png' }]
    } as ComponentDef;
    fixture.detectChanges();

    const scrollSpy = vi.spyOn(component, 'scrollCarousel');
    const compiled = fixture.nativeElement as HTMLElement;

    const prevButton = compiled.querySelector('.carousel-prev') as HTMLButtonElement;
    const nextButton = compiled.querySelector('.carousel-next') as HTMLButtonElement;

    prevButton.click();
    expect(scrollSpy).toHaveBeenCalledWith(-1, expect.any(HTMLElement));

    nextButton.click();
    expect(scrollSpy).toHaveBeenCalledWith(1, expect.any(HTMLElement));
  });
});
