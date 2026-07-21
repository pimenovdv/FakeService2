import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject } from 'rxjs';
import { Screen, Condition, ComponentDef, CrossValidationRule } from '../models/screen.model';

@Injectable({
  providedIn: 'root',
})
export class StateService {
  private currentScreenSubject = new BehaviorSubject<Screen | null>(null);
  public currentScreen$ = this.currentScreenSubject.asObservable();

  private componentDefsSubject = new BehaviorSubject<ComponentDef[]>([]);
  public componentDefs$ = this.componentDefsSubject.asObservable();

  private answersSubject = new BehaviorSubject<Record<string, any>>({});
  public answers$ = this.answersSubject.asObservable();

  public answerChanges$ = new Subject<{ componentId: string; value: any }>();

  private validationState: Record<string, boolean> = {};

  private submitAttemptedSubject = new BehaviorSubject<boolean>(false);
  public submitAttempted$ = this.submitAttemptedSubject.asObservable();

  constructor() {}

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.componentDefsSubject.next(screen.components || []);
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
    this.answerChanges$.next({ componentId, value });
  }

  restoreAnswers(savedAnswers: Record<string, any>) {
    this.answersSubject.next(savedAnswers);
  }

  updateComponentDef(componentId: string, updates: Partial<ComponentDef>) {
    const currentDefs = this.componentDefsSubject.value;
    const newDefs = currentDefs.map((def) => {
      if (def.id === componentId) {
        return { ...def, ...updates };
      }
      return def;
    });
    this.componentDefsSubject.next(newDefs);
  }

  getComponentDef(componentId: string): ComponentDef | undefined {
    return this.componentDefsSubject.value.find((def) => def.id === componentId);
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
    return Object.values(this.validationState).every((v) => v);
  }

  setSubmitAttempted(value: boolean) {
    this.submitAttemptedSubject.next(value);
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.componentDefsSubject.next([]);
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

  evaluateCrossValidations(rules: CrossValidationRule[] | undefined): string[] {
    if (!rules || rules.length === 0) {
      return [];
    }
    const errors: string[] = [];
    const answers = this.answersSubject.value;

    for (const rule of rules) {
      if (rule.type === 'match') {
        if (rule.fields && rule.fields.length > 1) {
          const firstValue = answers[rule.fields[0]];
          for (let i = 1; i < rule.fields.length; i++) {
            if (answers[rule.fields[i]] !== firstValue) {
              errors.push(rule.message);
              break;
            }
          }
        }
      } else if (rule.type === 'required_if') {
        if (rule.condition_field && rule.target_field) {
          const conditionValue = answers[rule.condition_field];
          if (conditionValue === rule.condition_value) {
            const targetValue = answers[rule.target_field];
            if (targetValue === null || targetValue === undefined || targetValue === '') {
              errors.push(rule.message);
            }
          }
        }
      }
    }
    return errors;
  }
}
