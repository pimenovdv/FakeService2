export type ControlType = 'text' | 'combobox' | 'checkbox' | 'radio' | 'datepicker' | 'textarea' | 'file' | 'number' | 'password' | 'slider' | 'color' | 'time' | 'toggle' | 'rating' | 'stepper';

export interface ValidationRule {
  type: 'required' | 'regex' | 'min' | 'max' | 'minLength' | 'maxLength';
  value?: any;
  message?: string;
}

export interface RestMetadata {
  endpoint: string;
  method: 'GET' | 'POST';
  params?: Record<string, string>;
}

export interface Condition {
  field: string;
  operator: '==' | '!=' | '>' | '<' | 'in';
  value: any;
}

export interface ComponentDef {
  id: string;
  type: ControlType;
  label: string;
  placeholder?: string;
  options?: any[]; // For static options in combobox/radio
  restMetadata?: RestMetadata; // For dynamic options fetching
  validations?: ValidationRule[];
  hidden?: boolean;
  disabled?: boolean;
  showIf?: Condition;
  disableIf?: Condition;
  accept?: string; // For file uploads
  multiple?: boolean; // For file uploads
  dependsOn?: string[]; // IDs of components this depends on
}

export interface ButtonDef {
  id: string;
  label: string;
  action: 'next_step' | 'cancel' | 'submit';
  color?: 'primary' | 'secondary' | 'warn';
}

export interface Screen {
  id: string;
  header: string;
  content: string;
  components: ComponentDef[];
  buttons: ButtonDef[];
}
