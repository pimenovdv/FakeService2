import { Component, Input, OnInit, OnChanges, SimpleChanges, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { ComponentDef } from '../../models/screen.model';

@Component({
  selector: 'app-audio-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './audio-control.html'
})
export class AudioControlComponent implements OnInit, OnChanges {
  @Input() def!: ComponentDef;
  @Input() value: any;

  safeUrl: SafeUrl | undefined;
  private sanitizer = inject(DomSanitizer);

  ngOnInit() {
    this.updateUrl();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['value']) {
      this.updateUrl();
    }
  }

  private updateUrl() {
    if (this.value) {
      this.safeUrl = this.sanitizer.bypassSecurityTrustUrl(this.value);
    } else {
      this.safeUrl = undefined;
    }
  }
}
