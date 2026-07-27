import { describe, it, expect, beforeEach, vi } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AudioControlComponent } from './audio-control';
import { ComponentDef } from '../../models/screen.model';

describe('AudioControlComponent', () => {
  let component: AudioControlComponent;
  let fixture: ComponentFixture<AudioControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AudioControlComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AudioControlComponent);
    component = fixture.componentInstance;

    const mockDef: ComponentDef = {
      id: 'audio_1',
      type: 'audio' as any,
      label: 'My Audio'
    };
    component.def = mockDef;
    component.value = 'https://example.com/audio.mp3';

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should sanitize url', () => {
    expect(component.safeUrl).toBeTruthy();
  });

  it('should render audio element', () => {
    const audio = fixture.nativeElement.querySelector('audio');
    expect(audio).toBeTruthy();
    expect(audio.src).toContain('example.com/audio.mp3');
  });
});
