import { Component, Input, OnChanges, SimpleChanges, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import * as dompurify from 'dompurify';
const DOMPurify = (dompurify as any).default || dompurify;

@Component({
  selector: 'app-alert-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './alert-control.html'
})
export class AlertControlComponent implements OnChanges, OnInit {
  @Input() def!: ComponentDef;
  @Input() value: any;

  safeHtml: SafeHtml | null = null;

  constructor(private sanitizer: DomSanitizer) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['value']) {
      this.updateSafeHtml();
    }
  }

  private updateSafeHtml(): void {
    if (this.value && typeof this.value === 'string' && (this.value.includes('<') || this.value.includes('>'))) {
        const clean = DOMPurify.sanitize(this.value);
        this.safeHtml = this.sanitizer.bypassSecurityTrustHtml(clean);
    } else {
        this.safeHtml = null;
    }
  }

  getAlertClasses(): string {
    const baseClasses = 'p-4 rounded-md border';
    const type = this.def.alertType || 'info';

    switch (type) {
      case 'success':
        return `${baseClasses} bg-green-50 border-green-400 text-green-700`;
      case 'warning':
        return `${baseClasses} bg-yellow-50 border-yellow-400 text-yellow-700`;
      case 'error':
        return `${baseClasses} bg-red-50 border-red-400 text-red-700`;
      case 'info':
      default:
        return `${baseClasses} bg-blue-50 border-blue-400 text-blue-700`;
    }
  }

  getAlertIcon(): string {
    const type = this.def.alertType || 'info';
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      case 'info':
      default: return 'ℹ';
    }
  }

  ngOnInit(): void {
    this.updateSafeHtml();
  }
}
