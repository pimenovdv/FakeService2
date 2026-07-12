import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Screen } from '../models/screen.model';

@Injectable({
  providedIn: 'root'
})
export class StateService {
  private currentScreenSubject = new BehaviorSubject<Screen | null>(null);
  public currentScreen$ = this.currentScreenSubject.asObservable();

  private answersSubject = new BehaviorSubject<Record<string, any>>({});
  public answers$ = this.answersSubject.asObservable();

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answersSubject.next({}); // Reset answers on new screen
  }

  getScreen(): Screen | null {
    return this.currentScreenSubject.value;
  }

  setAnswer(componentId: string, value: any) {
    const currentAnswers = { ...this.answersSubject.value };
    currentAnswers[componentId] = value;
    this.answersSubject.next(currentAnswers);
  }

  getAnswer(componentId: string): any {
    return this.answersSubject.value[componentId];
  }

  getAllAnswers(): Record<string, any> {
    return { ...this.answersSubject.value };
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answersSubject.next({});
  }

  evaluateCondition(condition?: { componentId: string, value: any }): boolean {
    if (!condition) {
      return false; // If no condition is defined, we can't evaluate it to true.
      // Callers should handle cases where condition is undefined themselves, typically treating it as false or default.
    }
    const currentAnswers = this.answersSubject.value;
    return currentAnswers[condition.componentId] === condition.value;
  }
}
