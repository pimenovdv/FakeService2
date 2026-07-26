import { describe, it, expect, beforeEach, vi } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SignaturePadControlComponent } from './signature-pad-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';

// Mock ResizeObserver
class ResizeObserverMock {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver = ResizeObserverMock as any;

describe('SignaturePadControlComponent', () => {
  let component: SignaturePadControlComponent;
  let fixture: ComponentFixture<SignaturePadControlComponent>;
  let stateServiceMock: any;

  const mockDef: ComponentDef = {
    id: 'test-signature',
    type: 'signature_pad',
    label: 'Sign Here'
  };

  beforeEach(async () => {
    stateServiceMock = {
      submitAttempted$: { subscribe: vi.fn() },
      setValidation: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [SignaturePadControlComponent],
      providers: [
        { provide: StateService, useValue: stateServiceMock }
      ]
    }).compileComponents();
  });

  beforeEach(() => {
    // Mock getContext for jsdom
    HTMLCanvasElement.prototype.getContext = vi.fn().mockReturnValue({
      scale: vi.fn(),
      clearRect: vi.fn(),
      fillRect: vi.fn(),
      beginPath: vi.fn(),
      moveTo: vi.fn(),
      lineTo: vi.fn(),
      stroke: vi.fn(),
      arc: vi.fn(),
      fill: vi.fn(),
      closePath: vi.fn(),
      getImageData: vi.fn().mockReturnValue({ data: [] }),
      putImageData: vi.fn()
    }) as any;

    fixture = TestBed.createComponent(SignaturePadControlComponent);
    component = fixture.componentInstance;
    component.def = mockDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should clear the pad and emit null on clear()', () => {
    const padSpy = vi.spyOn((component as any).signaturePad, 'clear');
    const valueSpy = vi.spyOn(component.valueChange, 'emit');

    component.clear();

    expect(padSpy).toHaveBeenCalled();
    expect(valueSpy).toHaveBeenCalledWith(null);
  });

  it('should correctly format undo on stroke', () => {
    const fromDataSpy = vi.spyOn((component as any).signaturePad, 'fromData');
    vi.spyOn((component as any).signaturePad, 'toData').mockReturnValue([{ color: 'black', points: [] } as any]);

    component.undo();

    expect(fromDataSpy).toHaveBeenCalledWith([]);
  });
});
