import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Screen, Condition } from '../models/screen.model';

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
    const currentAnswers = this.answersSubject.value;
    this.answersSubject.next({ ...currentAnswers, [componentId]: value });
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

  evaluateCondition(cond?: Condition): boolean {
    if (!cond) return true; // If no condition is provided, it always passes

    const value = this.getAnswer(cond.field);

    if (cond.hasValue !== undefined) {
      const isValuePresent = value !== undefined && value !== null && value !== '';
      if (cond.hasValue && !isValuePresent) return false;
      if (!cond.hasValue && isValuePresent) return false;
    }

    if (cond.equals !== undefined) {
      if (value !== cond.equals) return false;
    }

    return true;
  }
}
