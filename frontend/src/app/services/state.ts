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

  private validationSubject = new BehaviorSubject<Record<string, boolean>>({});
  public validation$ = this.validationSubject.asObservable();

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answersSubject.next({}); // Reset answers on new screen
    this.validationSubject.next({}); // Reset validation on new screen
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
    const currentValidation = this.validationSubject.value;
    const newValidation = { ...currentValidation, [componentId]: isValid };
    this.validationSubject.next(newValidation);
  }

  getValidationState(componentId: string): boolean {
    const validation = this.validationSubject.value;
    return validation[componentId] ?? false; // Default to false if not validated yet
  }

  isFormValid(components: { id: string, hidden?: boolean, disabled?: boolean, validations?: any[] }[]): boolean {
    const validation = this.validationSubject.value;
    for (const comp of components) {
      if (comp.hidden || comp.disabled) {
        continue;
      }

      // If it has no validations, it's valid by default.
      if (!comp.validations || comp.validations.length === 0) {
        continue;
      }

      if (validation[comp.id] === false || validation[comp.id] === undefined) {
        return false;
      }
    }
    return true;
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answersSubject.next({});
    this.validationSubject.next({});
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
