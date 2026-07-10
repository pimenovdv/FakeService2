import { Screen, ComponentDef, ButtonDef, ControlType } from './screen.model';

describe('Screen Models', () => {
  it('should be able to create a ComponentDef object', () => {
    const component: ComponentDef = {
      id: 'test-input',
      type: 'text' as ControlType,
      label: 'Test Input',
      placeholder: 'Enter text...',
      validations: [
        { type: 'required', message: 'This field is required' }
      ]
    };

    expect(component.id).toBe('test-input');
    expect(component.type).toBe('text');
    expect(component.label).toBe('Test Input');
    expect(component.placeholder).toBe('Enter text...');
    expect(component.validations?.length).toBe(1);
    expect(component.validations?.[0].type).toBe('required');
  });

  it('should be able to create a ButtonDef object', () => {
    const button: ButtonDef = {
      id: 'submit-btn',
      label: 'Submit',
      action: 'next_step',
      color: 'primary'
    };

    expect(button.id).toBe('submit-btn');
    expect(button.label).toBe('Submit');
    expect(button.action).toBe('next_step');
    expect(button.color).toBe('primary');
  });

  it('should be able to create a Screen object', () => {
    const screen: Screen = {
      id: 'screen-1',
      header: 'Welcome',
      content: 'Please fill out the form.',
      components: [
        {
          id: 'first-name',
          type: 'text',
          label: 'First Name'
        }
      ],
      buttons: [
        {
          id: 'next',
          label: 'Next',
          action: 'next_step'
        }
      ]
    };

    expect(screen.id).toBe('screen-1');
    expect(screen.header).toBe('Welcome');
    expect(screen.content).toBe('Please fill out the form.');
    expect(screen.components.length).toBe(1);
    expect(screen.components[0].id).toBe('first-name');
    expect(screen.buttons.length).toBe(1);
    expect(screen.buttons[0].id).toBe('next');
  });
});
