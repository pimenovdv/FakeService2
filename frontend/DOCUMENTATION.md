# Frontend Documentation

This document outlines the supported component types, validation rule formats, and REST metadata structures used in the Angular Screen Player.

## Supported Component Types (`ControlType`)

The player dynamically renders controls based on the `type` field defined in the `ComponentDef`. The supported types are:

*   **`text`**: A simple text input field. Supports `placeholder` and `regex` validation.
*   **`combobox`**: A dropdown selection control. Options can be static (provided in the `options` array) or dynamic (fetched using `restMetadata`).
*   **`checkbox`**: A single boolean checkbox.
*   **`radio`**: A set of mutually exclusive radio buttons. Options are static and provided in the `options` array.
*   **`datepicker`**: A date selection control.

## Validation Rule Formats (`ValidationRule`)

Validation rules are defined as an array of objects within a `ComponentDef`. Each rule dictates how the value of the control should be validated before the form can be submitted.

*   **`required`**: The field must have a non-empty value.
*   **`regex`**: The field's string value must match the provided regular expression.
    *   `value`: The regex string to match.
*   **`min`**: The value must be greater than or equal to the specified number or date.
    *   `value`: The minimum allowed value (number or date string).
*   **`max`**: The value must be less than or equal to the specified number or date.
    *   `value`: The maximum allowed value (number or date string).
*   **`minLength`**: The string value must have a length greater than or equal to this value.
    *   `value`: The minimum allowed length (number).
*   **`maxLength`**: The string value must have a length less than or equal to this value.
    *   `value`: The maximum allowed length (number).

All validation rules also support an optional `message` field, which can provide a custom error message to display if the validation fails.

## REST Metadata Structures (`RestMetadata`)

REST metadata is used by controls like the `combobox` to dynamically fetch their options from the backend API.

*   **`endpoint`**: The API endpoint path to call (e.g., `/api/data/countries`).
*   **`method`**: The HTTP method to use, typically `'GET'` or `'POST'`.
*   **`params`** (optional): A record (dictionary) of query parameters to include in the request. For example, `{"search": "query"}`.
