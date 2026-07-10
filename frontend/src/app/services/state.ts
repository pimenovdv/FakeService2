import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Screen } from '../models/screen.model';

@Injectable({
  providedIn: 'root'
})
export class StateService {
  private currentScreenSubject = new BehaviorSubject<Screen | null>(null);
  public currentScreen$ = this.currentScreenSubject.asObservable();

  private answers: Record<string, any> = {};

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answers = {}; // Reset answers on new screen
  }

  getScreen(): Screen | null {
    return this.currentScreenSubject.value;
  }

  setAnswer(componentId: string, value: any) {
    this.answers[componentId] = value;
  }

  getAnswer(componentId: string): any {
    return this.answers[componentId];
  }

  getAllAnswers(): Record<string, any> {
    return { ...this.answers };
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answers = {};
  }
}
