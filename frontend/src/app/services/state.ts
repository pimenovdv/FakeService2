import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Screen, ComponentDef, Condition } from '../models/screen.model';

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

  private evaluateConditions(conditions: Condition[] | undefined): boolean {
    if (!conditions || conditions.length === 0) {
      return false; // default is false (not hidden/disabled)
    }

    return conditions.every(condition => {
      const answer = this.getAnswer(condition.dependsOn);
      switch (condition.operator) {
        case '===': return answer === condition.value;
        case '!==': return answer !== condition.value;
        case '>': return Number(answer) > Number(condition.value);
        case '<': return Number(answer) < Number(condition.value);
        default: return false;
      }
    });
  }

  isComponentHidden(def: ComponentDef): boolean {
    if (def.hidden) return true;
    if (def.showConditions && def.showConditions.length > 0) {
      return !this.evaluateConditions(def.showConditions);
    }
    return false;
  }

  isComponentDisabled(def: ComponentDef): boolean {
    if (def.disabled) return true;
    if (def.disableConditions && def.disableConditions.length > 0) {
      return this.evaluateConditions(def.disableConditions);
    }
    return false;
  }
}
