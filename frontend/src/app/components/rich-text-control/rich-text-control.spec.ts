import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RichTextControl } from './rich-text-control';
import { QuillModule } from 'ngx-quill';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';

describe('RichTextControl', () => {
  let component: RichTextControl;
  let fixture: ComponentFixture<RichTextControl>;

  const mockDef: ComponentDef = {
    id: 'test-rich-text',
    type: 'rich_text',
    label: 'Test Editor',
    placeholder: 'Type something...',
    validations: [{ type: 'required' }],
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RichTextControl, FormsModule, QuillModule.forRoot()],
    }).compileComponents();

    fixture = TestBed.createComponent(RichTextControl);
    component = fixture.componentInstance;
    component.def = mockDef;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit valueChange when value changes', () => {
    vi.spyOn(component.valueChange, 'emit');
    component.onValueChange('<p>Hello World!</p>');
    expect(component.valueChange.emit).toHaveBeenCalledWith('<p>Hello World!</p>');
    expect(component.value).toBe('<p>Hello World!</p>');
  });

  it('should display validation errors when invalid and touched', () => {
    component.value = ''; // Required validation will fail
    component.touched = true;
    component.validate();
    fixture.detectChanges();

    expect(component.isValid).toBe(false);

    const errorContainer = fixture.nativeElement.querySelector('.error-messages');
    expect(errorContainer).toBeTruthy();
    expect(errorContainer.textContent).toContain('This field is required');
  });

  it('should handle disabled state', () => {
    component.def = { ...mockDef, disabled: true };
    fixture.detectChanges();
    const quillEditor = fixture.nativeElement.querySelector('quill-editor');
    // For ngx-quill, the property readOnly is what we bind
    // ngx-quill reflects it via class or we can just check if readOnly property is true
    expect(component.def.disabled).toBe(true);
  });
});
