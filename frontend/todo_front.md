# Frontend Development Plan (Angular Screen Player)

This document outlines the step-by-step development process for the Angular-based screen player application.

## Phase 1: Project Setup and Architecture
1. **Initialize Angular Project**
   - Setup Angular CLI, routing, and HTTP client.
   - Configure global styles, UI framework (e.g., Angular Material or Tailwind CSS).
2. **Define Data Models**
   - Create interfaces for the Screen definition JSON (`Screen`, `ComponentDef`, `ButtonDef`).
   - Define types for different controls (Text, ComboBox, Checkbox, Radio, DatePicker).
   - Define structure for validation rules and metadata.
3. **Core Services**
   - `ApiService`: Handle HTTP calls (`POST /start`, `POST /next_step`, and dynamic REST calls for components).
   - `StateService`: Manage the current state of the screen, user answers, and dependencies between components.

## Phase 2: Routing and Initialization
1. **Route Configuration**
   - Create route `/:service_id/1` mapped to the `PlayerComponent`.
2. **Player Component Initialization**
   - Read `service_id` from route parameters.
   - Call `ApiService.start(service_id)`.
   - Render loading state while waiting for the JSON response.
   - Parse the JSON response and initialize the `StateService` with screen data.

## Phase 3: Dynamic Component Rendering Engine
1. **Screen Layout Skeleton**
   - Create the main layout rendering `screen.header` and `screen.content`.
2. **Dynamic Component Loader**
   - Implement an Angular structural directive or component (`<app-dynamic-field>`) that takes a `ComponentDef` and dynamically instantiates the correct specific control component.
3. **Base Control Component**
   - Create a base class for all controls handling common logic: initialization, reading values, applying validation (Regex, required, etc.), and emitting value changes.

## Phase 4: Implementing Specific Controls
1. **Text Input Control**
   - Simple text field with regex validation and placeholder support.
2. **ComboBox / Select Control**
   - Dropdown with static options from JSON.
   - Support for dynamic options fetching via REST call metadata provided in JSON.
3. **Interactive/Dependent Controls**
   - Implement logic in `StateService` to evaluate conditions (e.g., if control A value is 'X', show control B).
   - Bind `disabled` and `hidden` properties of controls to state evaluations.
4. **Action Buttons**
   - Render buttons defined in the JSON.
   - Implement click handler to collect data, validate, and call `next_step`.

## Phase 5: Validation and Submission
1. **Form Validation Engine**
   - Collect all validation states from rendered components.
   - Prevent submission if validation fails.
2. **Next Step Submission**
   - Compile the `answers` dictionary (component ID -> value).
   - Merge `answers` with the original JSON or required payload structure.
   - Call `POST /next_step`.
   - Handle the response (load next screen or show completion message).

## Phase 6: Refinement and Testing
1. **Unit Tests**
   - Test data models, `StateService` logic, and dynamic component rendering.
2. **End-to-End Tests**
   - Simulate a user flow for a specific `service_id`, verifying component interactions and correct payload submission.
3. **Documentation**
   - Document supported component types, validation rule formats, and REST metadata structures in this directory.
