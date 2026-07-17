import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TagsControlComponent } from './tags-control';
import { ComponentDef } from '../../models/screen.model';
import { FormsModule } from '@angular/forms';

describe('TagsControlComponent', () => {
  let component: TagsControlComponent;
  let fixture: ComponentFixture<TagsControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TagsControlComponent, FormsModule],
    }).compileComponents();

    fixture = TestBed.createComponent(TagsControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize tags from array value', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.componentRef.setInput('value', ['angular', 'react']);
    fixture.detectChanges();
    component.ngOnInit();

    expect(component.tags).toEqual(['angular', 'react']);
  });

  it('should initialize tags from comma-separated string value', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.componentRef.setInput('value', 'angular, react, vue');
    fixture.detectChanges();
    component.ngOnInit();

    expect(component.tags).toEqual(['angular', 'react', 'vue']);
  });

  it('should add a tag on Enter', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.detectChanges();

    component.inputValue = 'svelte';
    component.onKeyDown(new KeyboardEvent('keydown', { key: 'Enter' }));

    expect(component.tags).toContain('svelte');
    expect(component.inputValue).toBe('');
  });

  it('should not add duplicate tags', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.componentRef.setInput('value', ['angular']);
    fixture.detectChanges();
    component.ngOnInit();

    component.inputValue = 'angular';
    component.addTag();

    expect(component.tags).toEqual(['angular']);
  });

  it('should remove a tag', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.componentRef.setInput('value', ['angular', 'react']);
    fixture.detectChanges();
    component.ngOnInit();

    component.removeTag(0);

    expect(component.tags).toEqual(['react']);
  });

  it('should emit value change on add', () => {
    fixture.componentRef.setInput('def', { id: 'tags1', type: 'tags', label: 'Tags' } as ComponentDef);
    fixture.detectChanges();

    let emittedValue: any;
    component.valueChange.subscribe((v) => emittedValue = v);

    component.inputValue = 'newtag';
    component.addTag();

    expect(emittedValue).toEqual(['newtag']);
  });

  it('should validate required rule', () => {
    fixture.componentRef.setInput('def', {
      id: 'tags1',
      type: 'tags',
      label: 'Tags',
      validations: [{ type: 'required', message: 'Req' }]
    } as ComponentDef);
    fixture.detectChanges();

    component.validate();
    expect(component.errors).toContain('Req');

    component.inputValue = 'test';
    component.addTag();
    component.validate();
    expect(component.errors.length).toBe(0);
  });
});
