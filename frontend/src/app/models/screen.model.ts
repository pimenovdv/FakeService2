export type ControlType = 'text' | 'combobox' | 'checkbox' | 'radio' | 'datepicker' | 'textarea' | 'file' | 'number' | 'password' | 'slider' | 'color' | 'time' | 'toggle' | 'rating' | 'stepper' | 'currency' | 'tags' | 'email' | 'phone' | 'url' | 'month' | 'search' | 'week' | 'datetime' | 'multiselect' | 'autocomplete' | 'button_group' | 'captcha' | 'progress' | 'markdown' | 'rich_text' | 'group' | 'data_table' | 'signature_pad' | 'barcode' | 'image' | 'divider' | 'iframe' | 'video' | 'audio' | 'alert';

export interface ValidationRule {
  type: 'required' | 'regex' | 'min' | 'max' | 'minLength' | 'maxLength' | 'step';
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
  tooltip?: string;
  helpText?: string;
  hidden?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  clearable?: boolean;
  autofocus?: boolean;
  mask?: string;
  showIf?: Condition;
  disableIf?: Condition;
  accept?: string; // For file uploads
  multiple?: boolean; // For file uploads
  currencySymbol?: string;
  enableDictation?: boolean;
  dependsOn?: string[]; // IDs of components this depends on
  components?: ComponentDef[]; // For grouped components
  altText?: string; // For images
  alertType?: 'info' | 'success' | 'warning' | 'error';
}

export interface ButtonDef {
  id: string;
  label: string;
  action: 'next_step' | 'cancel' | 'submit' | 'export_pdf';
  color?: 'primary' | 'secondary' | 'warn';
  confirmMessage?: string;
}

export interface ScriptDef {
  trigger: 'onLoad' | 'onChange';
  targetComponentId?: string;
  code: string;
}

export interface Theme {
  primaryColor?: string;
  backgroundColor?: string;
  textColor?: string;
  fontFamily?: string;
}

export interface CrossValidationRule {
  type: 'match' | 'required_if';
  fields?: string[]; // Used for 'match'
  condition_field?: string; // Used for 'required_if'
  condition_value?: any; // Used for 'required_if'
  target_field?: string; // Used for 'required_if'
  message: string;
}

export interface Screen {
  id: string;
  header: string;
  content: string;
  components: ComponentDef[];
  buttons: ButtonDef[];
  scripts?: ScriptDef[];
  crossValidations?: CrossValidationRule[];
  theme?: Theme;
}
