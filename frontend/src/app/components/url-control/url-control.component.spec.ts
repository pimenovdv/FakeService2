import { ComponentFixture, TestBed } from '@angular/core/testing';
import { UrlControlComponent } from './url-control.component';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('UrlControlComponent', () => {
  let component: UrlControlComponent;
  let fixture: ComponentFixture<UrlControlComponent>;

  const mockDef: ComponentDef = {
    id: 'testUrl',
    type: 'url',
    label: 'Website URL',
    placeholder: 'Enter website URL'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UrlControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(UrlControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', '');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display label and placeholder', async () => {
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    const label = compiled.querySelector('label');
    const input = compiled.querySelector('input');
    expect(label?.textContent).toContain('Website URL');
    expect(input?.placeholder).toBe('Enter website URL');
    expect(input?.type).toBe('url');
  });

  it('should update value on input change', async () => {
    const changeSpy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = 'https://example.com';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(changeSpy).toHaveBeenCalledWith('https://example.com');
  });

  it('should not render clear button when clearable is false', () => {
    fixture.componentRef.setInput('def', { ...mockDef, clearable: false });
    component.value = 'https://example.com';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeNull();
  });

  it('should render clear button when clearable is true and value exists', () => {
    fixture.componentRef.setInput('def', { ...mockDef, clearable: true });
    component.value = 'https://example.com';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeTruthy();
  });

  it('should clear value when clear button is clicked', () => {
    fixture.componentRef.setInput('def', { ...mockDef, clearable: true });
    component.value = 'https://example.com';
    fixture.detectChanges();

    let emittedValue: any;
    component.valueChange.subscribe(val => emittedValue = val);

    const clearBtn = fixture.nativeElement.querySelector('.clear-button') as HTMLButtonElement;
    clearBtn.click();

    expect(emittedValue).toBe('');
    expect(component.value).toBe('');
  });
});
