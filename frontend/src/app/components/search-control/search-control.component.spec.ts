import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SearchControlComponent } from './search-control.component';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('SearchControlComponent', () => {
  let component: SearchControlComponent;
  let fixture: ComponentFixture<SearchControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(SearchControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display label and render search input', () => {
    const def: ComponentDef = { id: 's1', type: 'search', label: 'Search Query' };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    const label = fixture.nativeElement.querySelector('label');
    expect(label.textContent).toContain('Search Query');

    const input = fixture.nativeElement.querySelector('input');
    expect(input.type).toBe('search');
  });

  it('should render required asterisk when required', () => {
    const def: ComponentDef = {
      id: 's1',
      type: 'search',
      label: 'Search Query',
      validations: [{ type: 'required' }]
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    const asterisk = fixture.nativeElement.querySelector('.required-asterisk');
    expect(asterisk).toBeTruthy();
  });

  it('should not render clear button when clearable is false', () => {
    const def: ComponentDef = { id: 's1', type: 'search', label: 'Search Query', clearable: false };
    fixture.componentRef.setInput('def', def);
    component.value = 'search text';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeNull();
  });

  it('should render clear button when clearable is true and value exists', () => {
    const def: ComponentDef = { id: 's1', type: 'search', label: 'Search Query', clearable: true };
    fixture.componentRef.setInput('def', def);
    component.value = 'search text';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeTruthy();
  });

  it('should not render clear button when clearable is true but value is empty', () => {
    const def: ComponentDef = { id: 's1', type: 'search', label: 'Search Query', clearable: true };
    fixture.componentRef.setInput('def', def);
    component.value = '';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeNull();
  });

  it('should clear value when clear button is clicked', () => {
    const def: ComponentDef = { id: 's1', type: 'search', label: 'Search Query', clearable: true };
    fixture.componentRef.setInput('def', def);
    component.value = 'search text';
    fixture.detectChanges();

    let emittedValue: any;
    component.valueChange.subscribe(val => emittedValue = val);

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    clearBtn.click();

    expect(emittedValue).toBe('');
    expect(component.value).toBe('');
  });
});
