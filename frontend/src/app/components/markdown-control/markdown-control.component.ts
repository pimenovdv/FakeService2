import { Component, Input, OnChanges, SimpleChanges, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

@Component({
  selector: 'app-markdown-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './markdown-control.component.html'
})
export class MarkdownControlComponent extends BaseControl implements OnChanges {
  @Input() override value: string = '';

  sanitizedHtml: SafeHtml = '';
  private sanitizer = inject(DomSanitizer);

  constructor() {
    super();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes['value'] || changes['def']) {
      this.renderMarkdown();
    }
  }

  override ngOnInit() {
    super.ngOnInit();
    this.renderMarkdown();
  }

  private renderMarkdown() {
    const rawMarkdown = this.value || this.def?.placeholder || '';
    const parsedHtml = marked.parse(rawMarkdown, { async: false }) as string;

    // Sanitize the HTML using DOMPurify
    const cleanHtml = DOMPurify.sanitize(parsedHtml);

    // It is safe to bypass Angular's sanitizer now because DOMPurify has already cleaned it.
    this.sanitizedHtml = this.sanitizer.bypassSecurityTrustHtml(cleanHtml);
  }
}