import { ComponentFixture, TestBed } from '@angular/core/testing';
import { VideoControlComponent } from './video-control';
import { ComponentDef } from '../../models/screen.model';

describe('VideoControlComponent', () => {
  let component: VideoControlComponent;
  let fixture: ComponentFixture<VideoControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VideoControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VideoControlComponent);
    component = fixture.componentInstance;

    const mockDef: ComponentDef = {
      id: 'video_1',
      type: 'video' as any,
      label: 'My Video'
    };
    component.def = mockDef;
    component.value = 'https://example.com/video.mp4';

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should sanitize url', () => {
    expect(component.safeUrl).toBeTruthy();
  });

  it('should render video element', () => {
    const video = fixture.nativeElement.querySelector('video');
    expect(video).toBeTruthy();
    expect(video.src).toContain('example.com/video.mp4');
  });
});
