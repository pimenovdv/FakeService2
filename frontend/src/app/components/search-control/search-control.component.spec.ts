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
});
