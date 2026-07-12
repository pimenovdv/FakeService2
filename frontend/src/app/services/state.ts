import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Screen, ComponentDef } from '../models/screen.model';

@Injectable({
  providedIn: 'root'
})
export class StateService {
  private currentScreenSubject = new BehaviorSubject<Screen | null>(null);
  public currentScreen$ = this.currentScreenSubject.asObservable();

  private answers: Record<string, any> = {};
  private validationStates: Record<string, boolean> = {};

  constructor() { }

  setScreen(screen: Screen) {
    this.currentScreenSubject.next(screen);
    this.answers = {}; // Reset answers on new screen
    this.validationStates = {};
  }

  getScreen(): Screen | null {
    return this.currentScreenSubject.value;
  }

  evaluateDependencies(def: ComponentDef): boolean {
    if (!def.dependsOn || def.dependsOn.length === 0) {
      return true;
    }
    return def.dependsOn.every(id => {
      const val = this.answers[id];
      return val !== null && val !== undefined && val !== '';
    });
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

  setValidationState(id: string, isValid: boolean) {
    this.validationStates[id] = isValid;
  }

  isScreenValid(): boolean {
    const screen = this.getScreen();
    if (!screen) {
      return false;
    }
    return screen.components.every(comp => {
      // If hidden/disabled due to dependencies, it might not need validation
      // But for simplicity, if evaluateDependencies is false, we consider it valid (ignored)
      if (!this.evaluateDependencies(comp)) {
        return true;
      }
      return this.validationStates[comp.id] !== false;
    });
  }

  clearState() {
    this.currentScreenSubject.next(null);
    this.answers = {};
    this.validationStates = {};
  }
}
