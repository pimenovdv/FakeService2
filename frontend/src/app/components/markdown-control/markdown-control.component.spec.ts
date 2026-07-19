import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MarkdownControlComponent } from './markdown-control.component';
import { StateService } from '../../services/state';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { By } from '@angular/platform-browser';

describe('MarkdownControlComponent', () => {
  let component: MarkdownControlComponent;
  let fixture: ComponentFixture<MarkdownControlComponent>;
  let mockStateService: any;

  beforeEach(async () => {
    mockStateService = {
      submitAttempted$: { subscribe: vi.fn() },
      setValidation: vi.fn(),
    };

    await TestBed.configureTestingModule({
      imports: [MarkdownControlComponent],
      providers: [{ provide: StateService, useValue: mockStateService }],
    }).compileComponents();

    fixture = TestBed.createComponent(MarkdownControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'md1', type: 'markdown', label: 'Markdown Viewer' };
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render markdown from value', async () => {
    component.def = { id: 'md1', type: 'markdown', label: 'Markdown Viewer' };
    fixture.componentRef.setInput('value', '# Hello World\nThis is **bold**.');
    fixture.detectChanges();
    await fixture.whenStable();

    const container = fixture.debugElement.query(By.css('.markdown-content')).nativeElement;
    expect(container.innerHTML).toContain('<h1>Hello World</h1>');
    expect(container.innerHTML).toContain('<strong>bold</strong>');
  });

  it('should render markdown from def.placeholder if value is empty', async () => {
    component.def = { id: 'md1', type: 'markdown', label: 'Markdown Viewer', placeholder: '*Italic text*' };
    fixture.detectChanges();
    await fixture.whenStable();

    const container = fixture.debugElement.query(By.css('.markdown-content')).nativeElement;
    expect(container.innerHTML).toContain('<em>Italic text</em>');
  });
});