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

  private validitiesSubject = new BehaviorSubject<Record<string, boolean>>({});

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answersSubject.next({}); // Reset answers on new screen
    this.validitiesSubject.next({}); // Reset validities
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

  setValidationState(componentId: string, isValid: boolean) {
    const currentValidities = this.validitiesSubject.value;
    const newValidities = { ...currentValidities, [componentId]: isValid };
    this.validitiesSubject.next(newValidities);
  }

  isScreenValid(): boolean {
    const validities = this.validitiesSubject.value;
    return Object.values(validities).every((v) => v === true);
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answersSubject.next({});
    this.validitiesSubject.next({});
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
