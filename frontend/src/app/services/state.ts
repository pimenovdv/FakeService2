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


  validateScreen(): boolean {
    const screen = this.getScreen();
    if (!screen) return true;

    const answers = this.answersSubject.value;
    let isValid = true;

    for (const comp of screen.components) {
      const isHidden = comp.hidden || (comp.showIf ? !this.evaluateCondition(comp.showIf) : false);
      const isDisabled = comp.disabled || (comp.disableIf ? this.evaluateCondition(comp.disableIf) : false);

      if (isHidden || isDisabled) {
        continue;
      }

      if (comp.validations) {
        const value = answers[comp.id];
        for (const rule of comp.validations) {
          switch (rule.type) {
            case 'required':
              if (value === null || value === undefined || value === '') {
                isValid = false;
              }
              break;
            case 'regex':
              if (value && rule.value) {
                const regex = new RegExp(rule.value);
                if (!regex.test(value.toString())) {
                  isValid = false;
                }
              }
              break;

            case 'min':
              if (value !== null && value !== undefined && value !== '' && rule.value !== undefined) {
                const v = isNaN(Date.parse(value)) ? Number(value) : Date.parse(value);
                const r = isNaN(Date.parse(rule.value)) ? Number(rule.value) : Date.parse(rule.value);
                if (v < r) {
                  isValid = false;
                }
              }
              break;

            case 'max':
              if (value !== null && value !== undefined && value !== '' && rule.value !== undefined) {
                const v = isNaN(Date.parse(value)) ? Number(value) : Date.parse(value);
                const r = isNaN(Date.parse(rule.value)) ? Number(rule.value) : Date.parse(rule.value);
                if (v > r) {
                  isValid = false;
                }
              }
              break;
            case 'minLength':
              if (value && rule.value !== undefined) {
                if (value.toString().length < Number(rule.value)) {
                  isValid = false;
                }
              }
              break;
            case 'maxLength':
              if (value && rule.value !== undefined) {
                if (value.toString().length > Number(rule.value)) {
                  isValid = false;
                }
              }
              break;
            case 'maxSize':
              if (value && value.size !== undefined && rule.value !== undefined) {
                if (value.size > Number(rule.value)) {
                  isValid = false;
                }
              }
              break;
            case 'allowedTypes':
              if (value && value.type !== undefined && rule.value !== undefined) {
                const types = Array.isArray(rule.value) ? rule.value : [rule.value];
                if (!types.includes(value.type)) {
                  isValid = false;
                }
              }
              break;
          }
        }
      }
    }

    return isValid;
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
