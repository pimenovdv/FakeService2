import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DividerControlComponent } from './divider-control';
import { ComponentDef } from '../../models/screen.model';

describe('DividerControlComponent', () => {
  let component: DividerControlComponent;
  let fixture: ComponentFixture<DividerControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DividerControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DividerControlComponent);
    component = fixture.componentInstance;

    const mockDef: ComponentDef = {
      id: 'divider_1',
      type: 'divider',
      label: 'Divider'
    };
    component.def = mockDef;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render hr element', () => {
    const hrElement = fixture.nativeElement.querySelector('hr');
    expect(hrElement).toBeTruthy();
  });
});
