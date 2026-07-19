import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ButtonGroupControlComponent } from './button-group-control.component';
import { describe, it, expect, beforeEach } from 'vitest';

describe('ButtonGroupControlComponent', () => {
  let component: ButtonGroupControlComponent;
  let fixture: ComponentFixture<ButtonGroupControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ButtonGroupControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ButtonGroupControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', {
      type: 'button_group',
      id: 'test_bg',
      label: 'Test Button Group',
      options: [
        { label: 'Option 1', value: 'opt1' },
        { label: 'Option 2', value: 'opt2' }
      ]
    });
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display options as buttons', () => {
    const buttons = fixture.nativeElement.querySelectorAll('button.group-button');
    expect(buttons.length).toBe(2);
    expect(buttons[0].textContent.trim()).toBe('Option 1');
    expect(buttons[1].textContent.trim()).toBe('Option 2');
  });

  it('should handle option selection', () => {
    const buttons = fixture.nativeElement.querySelectorAll('button.group-button');
    buttons[1].click();
    fixture.detectChanges();

    expect(component.value).toBe('opt2');

    // Check if selected class is applied
    const updatedButtons = fixture.nativeElement.querySelectorAll('button.group-button');
    expect(updatedButtons[1].classList.contains('selected')).toBe(true);
    expect(updatedButtons[0].classList.contains('selected')).toBe(false);
  });

  it('should respect disabled state', () => {
    fixture.componentRef.setInput('def', {
       ...component.def,
       disabled: true
    });
    fixture.detectChanges();

    const buttons = fixture.nativeElement.querySelectorAll('button.group-button');
    expect(buttons[0].disabled).toBe(true);

    buttons[1].click();
    fixture.detectChanges();
    // Assuming selectOption prevents updating value if disabled
    expect(component.value).toBeUndefined();
  });
});
