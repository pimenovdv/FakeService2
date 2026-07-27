import { describe, it, expect, beforeEach } from 'vitest';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ImageControlComponent } from './image-control';
import { StateService } from '../../services/state';
import { By } from '@angular/platform-browser';

describe('ImageControlComponent', () => {
  let component: ImageControlComponent;
  let fixture: ComponentFixture<ImageControlComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImageControlComponent],
      providers: [StateService]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ImageControlComponent);
    component = fixture.componentInstance;

    component.def = {
      id: 'test-image',
      type: 'image',
      label: 'Test Image',
      altText: 'A beautiful test image'
    };
  });

  it('should create', () => {
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should display image when value is set', () => {
    component.value = 'https://example.com/image.png';
    fixture.detectChanges();

    const imgEl = fixture.debugElement.query(By.css('img'));
    expect(imgEl).toBeTruthy();
    expect(imgEl.nativeElement.src).toBe('https://example.com/image.png');
    expect(imgEl.nativeElement.alt).toBe('A beautiful test image');
    expect(imgEl.nativeElement.id).toBe('test-image');
  });

  it('should display fallback alt text when altText is missing', () => {
    component.def = {
      id: 'test-image-2',
      type: 'image',
      label: 'Fallback Label Image'
    };
    component.value = 'https://example.com/image2.png';
    fixture.detectChanges();

    const imgEl = fixture.debugElement.query(By.css('img'));
    expect(imgEl.nativeElement.alt).toBe('Fallback Label Image');
  });

  it('should display fallback message when value is not set', () => {
    fixture.detectChanges();

    const imgEl = fixture.debugElement.query(By.css('img'));
    expect(imgEl).toBeFalsy();

    const noImageEl = fixture.debugElement.query(By.css('.text-gray-400'));
    expect(noImageEl).toBeTruthy();
    expect(noImageEl.nativeElement.textContent.trim()).toBe('No image available');
  });
});
