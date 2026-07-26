import { Component, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { BrowserMultiFormatReader } from '@zxing/browser';

@Component({
  selector: 'app-barcode-scanner-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './barcode-scanner-control.html',
  styleUrls: ['./barcode-scanner-control.css']
})
export class BarcodeScannerControlComponent extends BaseControl implements AfterViewInit, OnDestroy {
  @ViewChild('videoElement') videoElement!: ElementRef<HTMLVideoElement>;

  isScanning = false;
  hasCameras = false;
  scannerError: string | null = null;
  private codeReader: BrowserMultiFormatReader;

  constructor() {
    super();
    this.codeReader = new BrowserMultiFormatReader();
  }

  async ngAfterViewInit() {
    try {
      const videoInputDevices = await BrowserMultiFormatReader.listVideoInputDevices();
      this.hasCameras = videoInputDevices && videoInputDevices.length > 0;
    } catch (err) {
      console.error('Error listing cameras:', err);
      this.hasCameras = false;
    }
  }

  async startScan() {
    if (!this.hasCameras) {
      this.scannerError = 'No camera found';
      return;
    }

    this.isScanning = true;
    this.scannerError = null;

    try {
      const videoInputDevices = await BrowserMultiFormatReader.listVideoInputDevices();
      if (videoInputDevices.length === 0) {
        throw new Error('No video input devices found');
      }

      const selectedDeviceId = videoInputDevices[0].deviceId;

      await this.codeReader.decodeFromVideoDevice(
        selectedDeviceId,
        this.videoElement.nativeElement,
        (result, err) => {
          if (result) {
            this.handleScan(result.getText());
          }
          if (err && err.name !== 'NotFoundException') {
            console.warn('Scan error (ignored):', err);
          }
        }
      );
    } catch (err: any) {
      console.error('Camera start error:', err);
      this.scannerError = err.message || 'Error starting camera';
      this.isScanning = false;
    }
  }

  stopScan() {
    this.isScanning = false;
    try {
      if (this.codeReader && (this.codeReader as any).reset) {
        (this.codeReader as any).reset();
      }
      const videoElem = this.videoElement?.nativeElement;
      if (videoElem && videoElem.srcObject) {
         const stream = videoElem.srcObject as MediaStream;
         stream.getTracks().forEach(track => track.stop());
         videoElem.srcObject = null;
      }
    } catch (err) {
      console.error("Error stopping video stream:", err);
    }
  }

  handleScan(value: string) {
    this.value = value;
    this.onValueChange(value);
    this.stopScan();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    this.stopScan();
  }
}
