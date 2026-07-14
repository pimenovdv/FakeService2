import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CheckboxControlComponent } from './checkbox-control';
import { ComponentDef } from '../../models/screen.model';
import { vi, expect, describe, it, beforeEach } from 'vitest';

describe('CheckboxControlComponent', () => {
  let component: CheckboxControlComponent;
  let fixture: ComponentFixture<CheckboxControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CheckboxControlComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(CheckboxControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'chk1', type: 'checkbox', label: 'Check me' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });
});
