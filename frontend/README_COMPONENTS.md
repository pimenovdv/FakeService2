# Supported Components & Configuration

This document outlines the supported component types, validation rules, and REST metadata formats used by the Angular Screen Player.

## Supported Component Types (`ControlType`)

The frontend rendering engine dynamically builds forms based on the `type` property in the JSON schema.

*   `text`: A standard single-line text input field.
*   `combobox`: A dropdown select control. It can be populated statically via an `options` array or dynamically via `restMetadata`.
*   `checkbox` (Planned): A standard checkbox for boolean selections.
*   `radio` (Planned): A radio button group for mutually exclusive options.
*   `datepicker` (Planned): A date selection input.

## Validation Rule Formats

Validation rules are defined inside the `validations` array of a `ComponentDef`. The `StateService` evaluates these rules before allowing a screen to be submitted.

| Rule Type | Description | Required Value Property |
| :--- | :--- | :--- |
| `required` | Ensures the field is not empty, null, or undefined. | `None` |
| `regex` | Validates the input string against a provided regular expression. | `value: string` (The regex pattern) |
| `min` | Validates that a numeric input is greater than or equal to a minimum value. | `value: number` |
| `max` | Validates that a numeric input is less than or equal to a maximum value. | `value: number` |
| `minLength`| Validates that the input string length is at least the specified minimum. | `value: number` |
| `maxLength`| Validates that the input string length is no more than the specified maximum. | `value: number` |

Example:
```json
"validations": [
  { "type": "required", "message": "This field is required" },
  { "type": "regex", "value": "^[a-zA-Z]+$", "message": "Only letters are allowed" }
]
```

## `RestMetadata` Structure

The `RestMetadata` structure enables components (like `combobox`) to fetch dynamic data from an API to populate their options.

```typescript
export interface RestMetadata {
  endpoint: string; // The URL to call. If it doesn't start with 'http', it resolves relative to the proxy config.
  method: 'GET' | 'POST'; // The HTTP method to use.
  params?: Record<string, string>; // Optional parameters or body payload.
}
```

Example usage in JSON:
```json
"restMetadata": {
  "endpoint": "/api/data/countries",
  "method": "GET"
}
```

## Conditional Display and State (`Condition`)

Components can be dynamically hidden or disabled based on answers to other fields.

```typescript
export interface Condition {
  field: string; // The ID of the component to observe.
  operator: '==' | '!=' | '>' | '<' | 'in'; // The comparison operator.
  value: any; // The value to compare against.
}
```

This is mapped to the `showIf` and `disableIf` attributes on a `ComponentDef`.
