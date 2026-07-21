import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { DraftService, Draft } from '../../services/draft';

@Component({
  selector: 'app-drafts',
  imports: [CommonModule],
  templateUrl: './drafts.html',
  styleUrl: './drafts.scss'
})
export class DraftsComponent implements OnInit {
  drafts: Draft[] = [];

  private draftService = inject(DraftService);
  private cdr = inject(ChangeDetectorRef);
  private router = inject(Router);

  ngOnInit(): void {
    this.loadDrafts();
  }

  loadDrafts(): void {
    this.drafts = this.draftService.getAllDrafts();
    this.cdr.detectChanges();
  }

  resumeDraft(draft: Draft): void {
    this.router.navigate([draft.serviceId, '1'], { queryParams: { resume: 'true' } });
  }

  deleteDraft(draft: Draft): void {
    this.draftService.deleteDraft(draft.serviceId);
    this.loadDrafts();
  }
}
