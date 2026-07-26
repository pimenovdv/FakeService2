import { ComponentFixture, TestBed } from '@angular/core/testing';
import { BarcodeScannerControlComponent } from './barcode-scanner-control';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { BrowserMultiFormatReader } from '@zxing/browser';
import { vi } from 'vitest';

describe('BarcodeScannerControlComponent', () => {
  let component: BarcodeScannerControlComponent;
  let fixture: ComponentFixture<BarcodeScannerControlComponent>;

  const mockDef: ComponentDef = {
    id: 'test_barcode',
    type: 'barcode',
    label: 'Test Barcode',
    validations: [{ type: 'required' }]
  };

  beforeEach(async () => {
    // Mocking ZXing
    vi.spyOn(BrowserMultiFormatReader, 'listVideoInputDevices').mockResolvedValue([
      { deviceId: '1', kind: 'videoinput', label: 'Camera 1', groupId: 'g1' } as MediaDeviceInfo
    ]);

    await TestBed.configureTestingModule({
      imports: [BarcodeScannerControlComponent, FormsModule]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(BarcodeScannerControlComponent);
    component = fixture.componentInstance;
    component.def = mockDef;

    // Stub decodeFromVideoDevice
    (component as any).codeReader.decodeFromVideoDevice = vi.fn().mockImplementation((deviceId, videoElement, callback) => {
        // We will call the callback manually in tests
    });

    fixture.detectChanges();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should initialize cameras on AfterViewInit', async () => {
    await component.ngAfterViewInit();
    expect(component.hasCameras).toBe(true);
  });

  it('should set isScanning to true and call decodeFromVideoDevice on startScan', async () => {
    await component.ngAfterViewInit(); // make sure it has cameras
    component.videoElement = { nativeElement: document.createElement('video') } as any;
    await component.startScan();
    expect(component.isScanning).toBe(true);
    expect((component as any).codeReader.decodeFromVideoDevice).toHaveBeenCalled();
  });

  it('should handle scan correctly', () => {
    const spy = vi.spyOn(component, 'onValueChange');
    const stopSpy = vi.spyOn(component, 'stopScan');

    component.handleScan('12345');

    expect(component.value).toBe('12345');
    expect(spy).toHaveBeenCalledWith('12345');
    expect(stopSpy).toHaveBeenCalled();
  });

  it('should stop scan properly', () => {
    component.isScanning = true;
    component.stopScan();
    expect(component.isScanning).toBe(false);
  });

  it('should validate correctly based on base control', () => {
     component.value = null;
     component.onValueChange(null);
     expect(component.isValid).toBe(false);

     component.value = 'abc';
     component.onValueChange('abc');
     expect(component.isValid).toBe(true);
  });
});
