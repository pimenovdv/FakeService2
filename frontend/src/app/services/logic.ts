import { Injectable, inject } from '@angular/core';
import { StateService } from './state';
import { ApiService } from './api';
import Interpreter from 'js-interpreter';

@Injectable({
  providedIn: 'root',
})
export class LogicService {
  private stateService = inject(StateService);
  private apiService = inject(ApiService);

  execute(code: string, context?: any) {
    const initFunc = (interpreter: any, globalObject: any) => {
      // Expose stateService API to the sandbox
      const stateObj = interpreter.createObject(interpreter.OBJECT);
      interpreter.setProperty(globalObject, 'state', stateObj);

      const setAnswerWrapper = (componentId: string, value: any) => {
        this.stateService.setAnswer(componentId, interpreter.pseudoToNative(value));
      };
      interpreter.setProperty(
        stateObj,
        'setAnswer',
        interpreter.createNativeFunction(setAnswerWrapper),
      );

      const getAnswerWrapper = (componentId: string) => {
        const val = this.stateService.getAnswer(componentId);
        return interpreter.nativeToPseudo(val);
      };
      interpreter.setProperty(
        stateObj,
        'getAnswer',
        interpreter.createNativeFunction(getAnswerWrapper),
      );

      const updateComponentDefWrapper = (componentId: string, updates: any) => {
        this.stateService.updateComponentDef(componentId, interpreter.pseudoToNative(updates));
      };
      interpreter.setProperty(
        stateObj,
        'updateComponentDef',
        interpreter.createNativeFunction(updateComponentDefWrapper),
      );

      const isFormValidWrapper = () => {
        return interpreter.nativeToPseudo(this.stateService.isFormValid());
      };
      interpreter.setProperty(
        stateObj,
        'isFormValid',
        interpreter.createNativeFunction(isFormValidWrapper),
      );

      const getComponentDefWrapper = (componentId: string) => {
        return interpreter.nativeToPseudo(this.stateService.getComponentDef(componentId));
      };
      interpreter.setProperty(
        stateObj,
        'getComponentDef',
        interpreter.createNativeFunction(getComponentDefWrapper),
      );

      const getAllAnswersWrapper = () => {
        return interpreter.nativeToPseudo(this.stateService.getAllAnswers());
      };
      interpreter.setProperty(
        stateObj,
        'getAllAnswers',
        interpreter.createNativeFunction(getAllAnswersWrapper),
      );

      const evaluateConditionWrapper = (condition: any) => {
        return interpreter.nativeToPseudo(
          this.stateService.evaluateCondition(interpreter.pseudoToNative(condition)),
        );
      };
      interpreter.setProperty(
        stateObj,
        'evaluateCondition',
        interpreter.createNativeFunction(evaluateConditionWrapper),
      );

      const apiCallWrapper = (endpointUrl: any, method: any, params: any, callback: any) => {
         const meta = {
            endpoint: interpreter.pseudoToNative(endpointUrl),
            method: interpreter.pseudoToNative(method) || 'GET',
            params: interpreter.pseudoToNative(params) || {}
         };

         this.apiService.dynamicCall(meta).subscribe({
           next: (data) => {
             callback(interpreter.nativeToPseudo(data));
             runInterpreter();
           },
           error: (err) => {
             console.error('Logic async call failed', err);
             callback(interpreter.nativeToPseudo({ error: err.message }));
             runInterpreter();
           }
         });
      };
      interpreter.setProperty(globalObject, 'apiCall', interpreter.createAsyncFunction(apiCallWrapper));
    };

    let myInterpreter: any;
    const runInterpreter = () => {
      try {
        myInterpreter.run();
      } catch (e) {
        console.error('Error executing logic step:', e);
      }
    };

    try {
      myInterpreter = new Interpreter(code, initFunc);
      runInterpreter();
    } catch (e) {
      console.error('Error executing logic:', e);
    }
  }
}
