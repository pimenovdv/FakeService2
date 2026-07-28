from typing import Literal, List, Optional, Any, Dict
from pydantic import BaseModel, Field

ControlType = Literal['text', 'combobox', 'checkbox', 'radio', 'datepicker', 'textarea', 'file', 'number', 'password', 'slider', 'color', 'time', 'toggle', 'rating', 'stepper', 'currency', 'tags', 'email', 'phone', 'url', 'month', 'search', 'week', 'datetime', 'multiselect', 'autocomplete', 'button_group', 'captcha', 'progress', 'markdown', 'group', 'carousel']

class ValidationRule(BaseModel):
    type: Literal['required', 'regex', 'min', 'max', 'minLength', 'maxLength']
    value: Optional[Any] = None
    message: Optional[str] = None

class CrossValidationRule(BaseModel):
    type: Literal['match']
    fields: List[str]
    message: Optional[str] = None

class RestMetadata(BaseModel):
    endpoint: str
    method: Literal['GET', 'POST']
    params: Optional[Dict[str, str]] = None

class ComponentDef(BaseModel):
    id: str
    type: ControlType
    label: str
    placeholder: Optional[str] = None
    options: Optional[List[Any]] = None
    restMetadata: Optional[RestMetadata] = None
    validations: Optional[List[ValidationRule]] = None
    tooltip: Optional[str] = None
    helpText: Optional[str] = None
    hidden: Optional[bool] = False
    disabled: Optional[bool] = False
    readonly: Optional[bool] = False
    clearable: Optional[bool] = None
    accept: Optional[str] = None
    multiple: Optional[bool] = False
    currencySymbol: Optional[str] = None
    dependsOn: Optional[List[str]] = None
    components: Optional[List['ComponentDef']] = None

class ButtonDef(BaseModel):
    id: str
    label: str
    action: Literal['next_step', 'previous_step', 'cancel', 'submit']
    color: Optional[Literal['primary', 'secondary', 'warn']] = None
    confirmMessage: Optional[str] = None

class ScriptDef(BaseModel):
    trigger: Literal['onLoad', 'onChange']
    targetComponentId: Optional[str] = None
    code: str

class ThemeDef(BaseModel):
    primaryColor: Optional[str] = None
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    fontFamily: Optional[str] = None

class ScreenDef(BaseModel):
    id: str
    header: str
    content: str
    components: List[ComponentDef]
    buttons: List[ButtonDef]
    crossValidations: Optional[List[CrossValidationRule]] = None
    scripts: Optional[List[ScriptDef]] = None
    theme: Optional[ThemeDef] = None
