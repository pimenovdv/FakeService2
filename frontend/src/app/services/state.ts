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

  private validationState: Record<string, boolean> = {};

  private submitAttemptedSubject = new BehaviorSubject<boolean>(false);
  public submitAttempted$ = this.submitAttemptedSubject.asObservable();

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answersSubject.next({}); // Reset answers on new screen
    this.validationState = {};
    this.submitAttemptedSubject.next(false);
  }

  getScreen(): Screen | null {
    return this.currentScreenSubject.value;
  }

  setAnswer(componentId: string, value: any) {
    const currentAnswers = this.answersSubject.value;
    const newAnswers = { ...currentAnswers, [componentId]: value };
    this.answersSubject.next(newAnswers);
  }

  getAnswer(componentId: string): any {
    return this.answersSubject.value[componentId];
  }

getAllAnswers(): Record<string, any> {
    return { ...this.answersSubject.value };
  }

  setValidation(id: string, valid: boolean) {
    this.validationState[id] = valid;
  }

  isFormValid(): boolean {
    return Object.values(this.validationState).every(v => v);
  }

  setSubmitAttempted(value: boolean) {
    this.submitAttemptedSubject.next(value);
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answersSubject.next({});
    this.validationState = {};
    this.submitAttemptedSubject.next(false);
  }

  evaluateCondition(condition: Condition | undefined): boolean {
    if (!condition) {
      return false; // Default if no condition
    }
    const currentAnswers = this.answersSubject.value;
    const fieldValue = currentAnswers[condition.field];

    switch (condition.operator) {
      case '==':
        return fieldValue === condition.value;
      case '!=':
        return fieldValue !== condition.value;
      case '>':
        return fieldValue > condition.value;
      case '<':
        return fieldValue < condition.value;
      case 'in':
        if (Array.isArray(condition.value)) {
          return condition.value.includes(fieldValue);
        }
        return false;
      default:
        return false;
    }
  }
}
