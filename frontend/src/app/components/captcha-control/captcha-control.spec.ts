import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CaptchaControlComponent } from './captcha-control.component';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { FormsModule } from '@angular/forms';

describe('CaptchaControlComponent', () => {
  let component: CaptchaControlComponent;
  let fixture: ComponentFixture<CaptchaControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CaptchaControlComponent, FormsModule],
      providers: [StateService]
    }).compileComponents();

    fixture = TestBed.createComponent(CaptchaControlComponent);
    component = fixture.componentInstance;

    // Set a basic valid def
    const def: ComponentDef = {
      id: 'captcha1',
      type: 'captcha',
      label: 'Security Check',
      validations: []
    };
    fixture.componentRef.setInput('def', def);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should generate a 6-character captcha on init', () => {
    expect(component.captchaText.length).toBe(6);
  });

  it('should regenerate captcha and clear value on refresh', () => {
    const originalCaptcha = component.captchaText;
    component.onValueChange('test');
    expect(component.value).toBe('test');

    const event = new Event('click');
    component.refreshCaptcha(event);

    expect(component.captchaText).not.toBe(originalCaptcha); // Small chance of failure if random string matches, but unlikely for 6 chars
    expect(component.captchaText.length).toBe(6);
    expect(component.value).toBe('');
  });

  it('should be valid if empty and not required', () => {
    component.onValueChange('');
    expect(component.isValid).toBe(true);
  });

  it('should be invalid if input does not match captcha', () => {
    component.onValueChange('wrong');
    expect(component.isValid).toBe(false);
    expect(component.errors).toContain('CAPTCHA does not match');
  });

  it('should be valid if input matches captcha', () => {
    component.onValueChange(component.captchaText);
    expect(component.isValid).toBe(true);
    expect(component.errors.length).toBe(0);
  });

  it('should evaluate required validation', () => {
    const requiredDef: ComponentDef = {
      id: 'captcha2',
      type: 'captcha',
      label: 'Sec',
      validations: [{ type: 'required' }]
    };
    fixture.componentRef.setInput('def', requiredDef);
    component.onValueChange('');
    expect(component.isValid).toBe(false);
    expect(component.errors).toContain('This field is required');
  });
});
