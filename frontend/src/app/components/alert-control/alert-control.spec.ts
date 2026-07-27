import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AlertControlComponent } from './alert-control';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';

describe('AlertControlComponent', () => {
  let component: AlertControlComponent;
  let fixture: ComponentFixture<AlertControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlertControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(AlertControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'alert1', type: 'alert' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render default info alert', () => {
    component.def = { id: 'alert1', type: 'alert', label: 'Info Alert' } as ComponentDef;
    component.value = 'This is an info message.';
    fixture.detectChanges();

    const alertEl = fixture.debugElement.query(By.css('div[role="alert"]')).nativeElement;
    expect(alertEl.className).toContain('bg-blue-50');
    expect(alertEl.className).toContain('border-blue-400');
    expect(alertEl.className).toContain('text-blue-700');
    expect(alertEl.textContent).toContain('ℹ');
    expect(alertEl.textContent).toContain('Info Alert');
    expect(alertEl.textContent).toContain('This is an info message.');
  });

  it('should render success alert', () => {
    component.def = { id: 'alert2', type: 'alert', alertType: 'success' } as ComponentDef;
    fixture.detectChanges();

    const alertEl = fixture.debugElement.query(By.css('div[role="alert"]')).nativeElement;
    expect(alertEl.className).toContain('bg-green-50');
    expect(alertEl.textContent).toContain('✓');
  });

  it('should render warning alert', () => {
    component.def = { id: 'alert3', type: 'alert', alertType: 'warning' } as ComponentDef;
    fixture.detectChanges();

    const alertEl = fixture.debugElement.query(By.css('div[role="alert"]')).nativeElement;
    expect(alertEl.className).toContain('bg-yellow-50');
    expect(alertEl.textContent).toContain('⚠');
  });

  it('should render error alert', () => {
    component.def = { id: 'alert4', type: 'alert', alertType: 'error' } as ComponentDef;
    fixture.detectChanges();

    const alertEl = fixture.debugElement.query(By.css('div[role="alert"]')).nativeElement;
    expect(alertEl.className).toContain('bg-red-50');
    expect(alertEl.textContent).toContain('✗');
  });

  it('should render safe HTML content', async () => {
    component.def = { id: 'alert5', type: 'alert' } as ComponentDef;
    component.value = '<strong>Bold text</strong><script>alert(1)</script>';
    fixture.detectChanges();
    await fixture.whenStable();

    const spanEl = fixture.debugElement.query(By.css('.html-text')).nativeElement;
    expect(spanEl.innerHTML).toContain('<strong>Bold text</strong>');
    expect(spanEl.innerHTML).not.toContain('<script>');
  });
});
