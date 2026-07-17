import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CurrencyControlComponent } from './currency-control';
import { StateService } from '../../services/state';
import { FormsModule } from '@angular/forms';
import { describe, it, expect, beforeEach } from 'vitest';

describe('CurrencyControlComponent', () => {
  let component: CurrencyControlComponent;
  let fixture: ComponentFixture<CurrencyControlComponent>;
  let stateService: StateService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CurrencyControlComponent, FormsModule],
      providers: [StateService]
    }).compileComponents();

    fixture = TestBed.createComponent(CurrencyControlComponent);
    component = fixture.componentInstance;
    stateService = TestBed.inject(StateService);
  });

  it('should create', () => {
    fixture.componentRef.setInput('def', { id: 'c1', type: 'currency', label: 'Currency', currencySymbol: '$' });
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render the currency symbol', async () => {
    fixture.componentRef.setInput('def', { id: 'c1', type: 'currency', label: 'Currency', currencySymbol: '€' });
    fixture.detectChanges();
    await fixture.whenStable();

    const el = fixture.nativeElement as HTMLElement;
    const symbolEl = el.querySelector('.currency-symbol');
    expect(symbolEl?.textContent?.trim()).toBe('€');
  });

  it('should emit value changes', () => {
    fixture.componentRef.setInput('def', { id: 'c1', type: 'currency', label: 'Currency' });
    let emittedVal: any;
    component.valueChange.subscribe(v => emittedVal = v);

    component.onValueChange(123.45);

    expect(emittedVal).toBe(123.45);
    expect(component.value).toBe(123.45);
  });
});
