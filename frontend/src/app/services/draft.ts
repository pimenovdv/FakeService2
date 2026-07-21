import { Injectable } from '@angular/core';
import { Screen } from '../models/screen.model';

export interface Draft {
  serviceId: string;
  screen: Screen;
  answers: Record<string, any>;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class DraftService {
  private readonly DRAFTS_KEY = 'app_drafts';

  constructor() { }

  getAllDrafts(): Draft[] {
    const draftsStr = localStorage.getItem(this.DRAFTS_KEY);
    if (draftsStr) {
      try {
        const draftsDict: Record<string, Draft> = JSON.parse(draftsStr);
        return Object.values(draftsDict).sort((a, b) => b.timestamp - a.timestamp);
      } catch (e) {
        console.error('Failed to parse drafts from localStorage', e);
        return [];
      }
    }
    return [];
  }

  getDraft(serviceId: string): Draft | null {
    const draftsStr = localStorage.getItem(this.DRAFTS_KEY);
    if (draftsStr) {
      try {
        const draftsDict: Record<string, Draft> = JSON.parse(draftsStr);
        return draftsDict[serviceId] || null;
      } catch (e) {
        console.error('Failed to parse drafts from localStorage', e);
        return null;
      }
    }
    return null;
  }

  saveDraft(serviceId: string, screen: Screen, answers: Record<string, any>): void {
    const draftsStr = localStorage.getItem(this.DRAFTS_KEY);
    let draftsDict: Record<string, Draft> = {};
    if (draftsStr) {
      try {
        draftsDict = JSON.parse(draftsStr);
      } catch (e) {
        console.error('Failed to parse drafts from localStorage', e);
      }
    }

    draftsDict[serviceId] = {
      serviceId,
      screen,
      answers,
      timestamp: Date.now()
    };

    localStorage.setItem(this.DRAFTS_KEY, JSON.stringify(draftsDict));
  }

  deleteDraft(serviceId: string): void {
    const draftsStr = localStorage.getItem(this.DRAFTS_KEY);
    if (draftsStr) {
      try {
        const draftsDict: Record<string, Draft> = JSON.parse(draftsStr);
        if (draftsDict[serviceId]) {
          delete draftsDict[serviceId];
          localStorage.setItem(this.DRAFTS_KEY, JSON.stringify(draftsDict));
        }
      } catch (e) {
        console.error('Failed to parse drafts from localStorage', e);
      }
    }
  }
}
