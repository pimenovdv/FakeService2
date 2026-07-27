import { Component, Input, OnInit, OnChanges, SimpleChanges, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';
import { ComponentDef } from '../../models/screen.model';

@Component({
  selector: 'app-iframe-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './iframe-control.html'
})
export class IframeControlComponent implements OnInit, OnChanges {
  @Input() def!: ComponentDef;
  @Input() value: any;

  safeUrl: SafeResourceUrl | undefined;
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
      this.safeUrl = this.sanitizer.bypassSecurityTrustResourceUrl(this.value);
    } else {
      this.safeUrl = undefined;
    }
  }
}
