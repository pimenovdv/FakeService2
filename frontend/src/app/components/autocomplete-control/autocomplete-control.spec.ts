import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AutocompleteControlComponent } from './autocomplete-control';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { describe, it, expect, beforeEach, afterEach } from 'vitest';

describe('AutocompleteControlComponent', () => {
  let component: AutocompleteControlComponent;
  let fixture: ComponentFixture<AutocompleteControlComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AutocompleteControlComponent, HttpClientTestingModule, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(AutocompleteControlComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load static options', () => {
    const def: ComponentDef = {
      id: 'auto1',
      type: 'autocomplete',
      label: 'Auto 1',
      options: ['Apple', 'Banana', 'Cherry']
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    expect(component.options).toEqual(['Apple', 'Banana', 'Cherry']);
    const datalist = fixture.nativeElement.querySelector('datalist');
    expect(datalist).toBeTruthy();
    expect(datalist.id).toBe('datalist-auto1');
    const options = datalist.querySelectorAll('option');
    expect(options.length).toBe(3);
  });

  it('should load dynamic options via GET', async () => {
    const def: ComponentDef = {
      id: 'auto2',
      type: 'autocomplete',
      label: 'Auto 2',
      restMetadata: {
        endpoint: '/api/data',
        method: 'GET'
      }
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();

    const req = httpMock.expectOne('/api/data');
    expect(req.request.method).toBe('GET');
    req.flush([{ label: 'One', value: '1' }, { label: 'Two', value: '2' }]);

    expect(component.options.length).toBe(2);
    await fixture.whenStable();
    fixture.detectChanges();

    const options = fixture.nativeElement.querySelectorAll('datalist option');
    expect(options.length).toBe(2);
    expect(options[0].value).toBe('1');
    expect(options[0].textContent).toBe('One');
  });

  it('should emit value changes', async () => {
    const def: ComponentDef = {
      id: 'auto3',
      type: 'autocomplete',
      label: 'Auto 3'
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();
    await fixture.whenStable();

    let emittedValue: any;
    component.valueChange.subscribe(val => emittedValue = val);

    const input = fixture.nativeElement.querySelector('input');
    input.value = 'test val';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(emittedValue).toBe('test val');
  });
});
