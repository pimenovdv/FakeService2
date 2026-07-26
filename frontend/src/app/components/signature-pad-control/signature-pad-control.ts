import { Component, ElementRef, ViewChild, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';
import SignaturePad from 'signature_pad';

@Component({
  selector: 'app-signature-pad-control',
  imports: [CommonModule],
  templateUrl: './signature-pad-control.html'
})
export class SignaturePadControlComponent extends BaseControl implements AfterViewInit, OnDestroy {
  @ViewChild('signatureCanvas') signatureCanvas!: ElementRef<HTMLCanvasElement>;
  private signaturePad?: SignaturePad;
  private resizeObserver?: ResizeObserver;

  ngAfterViewInit() {
    this.signaturePad = new SignaturePad(this.signatureCanvas.nativeElement, {
      backgroundColor: 'rgb(255, 255, 255)' // essential for saving to jpeg/jpg if needed, and good default
    });

    this.signaturePad.addEventListener('endStroke', () => {
      this.updateValue();
    });

    // Resize canvas correctly on window resize or layout changes
    this.resizeObserver = new ResizeObserver(() => this.resizeCanvas());
    this.resizeObserver.observe(this.signatureCanvas.nativeElement.parentElement as Element);

    // Initial resize to ensure correct bounds
    setTimeout(() => this.resizeCanvas(), 0);
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    this.resizeObserver?.disconnect();
    this.signaturePad?.off();
  }

  private resizeCanvas() {
    if (!this.signatureCanvas) return;

    const canvas = this.signatureCanvas.nativeElement;
    const ratio = Math.max(window.devicePixelRatio || 1, 1);

    // This part causes the canvas to be cleared
    canvas.width = canvas.offsetWidth * ratio;
    canvas.height = canvas.offsetHeight * ratio;
    canvas.getContext('2d')?.scale(ratio, ratio);

    if (this.signaturePad) {
      this.signaturePad.clear(); // otherwise isEmpty() might return incorrect value
      if (this.value) {
        this.signaturePad.fromDataURL(this.value);
      }
    }
  }

  clear() {
    this.signaturePad?.clear();
    this.onValueChange(null);
  }

  undo() {
    if (!this.signaturePad) return;

    const data = this.signaturePad.toData();
    if (data) {
      data.pop(); // remove the last dot or line
      this.signaturePad.fromData(data);
      this.updateValue();
    }
  }

  private updateValue() {
    if (this.signaturePad && !this.signaturePad.isEmpty()) {
      this.onValueChange(this.signaturePad.toDataURL());
    } else {
      this.onValueChange(null);
    }
  }
}