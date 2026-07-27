import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IframeControlComponent } from './iframe-control';
import { ComponentDef } from '../../models/screen.model';

describe('IframeControlComponent', () => {
  let component: IframeControlComponent;
  let fixture: ComponentFixture<IframeControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IframeControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IframeControlComponent);
    component = fixture.componentInstance;

    const mockDef: ComponentDef = {
      id: 'iframe_1',
      type: 'iframe' as any,
      label: 'My Iframe'
    };
    component.def = mockDef;
    component.value = 'https://example.com';

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should sanitize url', () => {
    expect(component.safeUrl).toBeTruthy();
  });

  it('should render iframe element', () => {
    const iframe = fixture.nativeElement.querySelector('iframe');
    expect(iframe).toBeTruthy();
    expect(iframe.src).toContain('example.com');
  });
});
