import { Component, OnInit, OnDestroy, NgZone, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { AutofocusDirective } from '../../directives/autofocus.directive';

@Component({
  selector: 'app-textarea-control',
  standalone: true,
  imports: [CommonModule, FormsModule, AutofocusDirective],
  templateUrl: './textarea-control.html',
  styleUrls: ['./textarea-control.scss']
})
export class TextareaControlComponent extends BaseControl implements OnInit, OnDestroy {
  isDictating = false;
  private recognition: any;
  private ngZone = inject(NgZone);

  override ngOnInit() {
    super.ngOnInit();
    this.initSpeechRecognition();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  private initSpeechRecognition() {
    if (this.def.enableDictation && typeof window !== 'undefined') {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;

        this.recognition.onstart = () => {
          this.ngZone.run(() => {
            this.isDictating = true;
          });
        };

        this.recognition.onresult = (event: any) => {
          this.ngZone.run(() => {
            const transcript = event.results[0][0].transcript;
            const currentValue = this.value ? this.value + ' ' : '';
            this.onValueChange(currentValue + transcript);
          });
        };

        this.recognition.onerror = (event: any) => {
          this.ngZone.run(() => {
            console.error('Speech recognition error', event.error);
            this.isDictating = false;
          });
        };

        this.recognition.onend = () => {
          this.ngZone.run(() => {
            this.isDictating = false;
          });
        };
      } else {
        console.warn('Speech recognition not supported in this browser.');
      }
    }
  }

  toggleDictation() {
    if (!this.recognition) {
      return;
    }

    if (this.isDictating) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }
}
