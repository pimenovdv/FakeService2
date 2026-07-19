from typing import Literal, List, Optional, Any, Dict
from pydantic import BaseModel, Field

ControlType = Literal['text', 'combobox', 'checkbox', 'radio', 'datepicker', 'textarea', 'file', 'number', 'password', 'slider', 'color', 'time', 'toggle', 'rating', 'stepper', 'currency', 'tags', 'email', 'phone', 'url', 'month', 'search', 'week', 'datetime', 'multiselect', 'autocomplete', 'button_group', 'captcha', 'progress', 'markdown']

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
    hidden: Optional[bool] = False
    disabled: Optional[bool] = False
    accept: Optional[str] = None
    multiple: Optional[bool] = False
    currencySymbol: Optional[str] = None
    dependsOn: Optional[List[str]] = None

class ButtonDef(BaseModel):
    id: str
    label: str
    action: Literal['next_step', 'previous_step', 'cancel', 'submit']
    color: Optional[Literal['primary', 'secondary', 'warn']] = None

class ScreenDef(BaseModel):
    id: str
    header: str
    content: str
    components: List[ComponentDef]
    buttons: List[ButtonDef]
    crossValidations: Optional[List[CrossValidationRule]] = None
