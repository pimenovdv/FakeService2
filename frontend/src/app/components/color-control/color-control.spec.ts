import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ColorControlComponent } from './color-control';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('ColorControlComponent', () => {
  let component: ColorControlComponent;
  let fixture: ComponentFixture<ColorControlComponent>;

  const mockDef: ComponentDef = {
    id: 'favColor',
    type: 'color',
    label: 'Favorite Color',
    validations: [{ type: 'required' }]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ColorControlComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ColorControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render color input with initial value', async () => {
    fixture.componentRef.setInput('value', '#ff0000');
    fixture.detectChanges();
    await fixture.whenStable();

    const input = fixture.debugElement.query(By.css('input[type="color"]'));
    expect(input).toBeTruthy();
    expect(input.nativeElement.value).toBe('#ff0000');
  });

  it('should emit value change on input', () => {
    const emitSpy = vi.spyOn(component.valueChange, 'emit');
    const input = fixture.debugElement.query(By.css('input[type="color"]'));

    input.nativeElement.value = '#00ff00';
    input.nativeElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect(emitSpy).toHaveBeenCalledWith('#00ff00');
  });

  it('should validate required correctly', () => {
    component.onValueChange('#0000ff');
    expect(component.isValid).toBe(true);

    component.onValueChange(null);
    expect(component.isValid).toBe(false);
  });
});
