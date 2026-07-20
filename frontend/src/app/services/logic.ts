import { Injectable, inject } from '@angular/core';
import { StateService } from './state';
import Interpreter from 'js-interpreter';

@Injectable({
  providedIn: 'root'
})
export class LogicService {
  private stateService = inject(StateService);

  execute(code: string, context?: any) {
    const initFunc = (interpreter: any, globalObject: any) => {
      // Expose stateService API to the sandbox
      const stateObj = interpreter.createObject(interpreter.OBJECT);
      interpreter.setProperty(globalObject, 'state', stateObj);

      const setAnswerWrapper = (componentId: string, value: any) => {
        this.stateService.setAnswer(componentId, interpreter.pseudoToNative(value));
      };
      interpreter.setProperty(stateObj, 'setAnswer', interpreter.createNativeFunction(setAnswerWrapper));

      const getAnswerWrapper = (componentId: string) => {
        const val = this.stateService.getAnswer(componentId);
        return interpreter.nativeToPseudo(val);
      };
      interpreter.setProperty(stateObj, 'getAnswer', interpreter.createNativeFunction(getAnswerWrapper));

      const updateComponentDefWrapper = (componentId: string, updates: any) => {
        this.stateService.updateComponentDef(componentId, interpreter.pseudoToNative(updates));
      };
      interpreter.setProperty(stateObj, 'updateComponentDef', interpreter.createNativeFunction(updateComponentDefWrapper));

      const isFormValidWrapper = () => {
        return interpreter.nativeToPseudo(this.stateService.isFormValid());
      };
      interpreter.setProperty(stateObj, 'isFormValid', interpreter.createNativeFunction(isFormValidWrapper));
    };

    try {
      const myInterpreter = new Interpreter(code, initFunc);
      myInterpreter.run();
    } catch (e) {
      console.error('Error executing logic:', e);
    }
  }
}
