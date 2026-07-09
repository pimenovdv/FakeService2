# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

## Phase 1: Project Setup and Environment
1. **Initialize Project**
   - Create a virtual environment (`uv` or `venv`).
   - Install dependencies: `playwright` (or similar for SSR/headless browser), `langchain` (or preferred LLM library), `openai` (or specific LLM provider SDK), `beautifulsoup4` (for HTML parsing).
2. **Configure Playwright**
   - Run `playwright install` to setup browsers.
   - Create basic initialization script to launch a headless browser and navigate to the frontend URL (e.g., `http://localhost:4200/{service_id}/1`).

## Phase 2: SSR HTML Extraction and State Management
1. **Render and Extract**
   - Wait for the Angular application to fully load (wait for specific DOM elements or network idle).
   - Extract the fully rendered HTML of the screen.
2. **Parse HTML Context**
   - Parse the HTML to identify input fields, labels, comboboxes, buttons, and validation rules present in the DOM.
   - Build a structured representation of the current screen's requirements (what fields need to be filled).

## Phase 3: LLM Integration and Conversation Loop
1. **Prompt Engineering**
   - Design system prompts for the LLM to understand its role: "You are an agent helping a user fill out a form. The form requires the following fields: {parsed_fields}. Ask the user for this information, use autocomplete features when available, and determine the values to input."
2. **Interactive Chat Loop**
   - Implement a CLI or simple API chat interface for the user.
   - Send the current form state and user input to the LLM.
   - The LLM should decide whether to ask the user a clarifying question or to execute actions on the form.

## Phase 4: Form Interaction and Autocomplete Handling
1. **Executing LLM Actions via Playwright**
   - Create Python functions that the LLM can call (function calling/tools) to interact with the DOM: `fill_input(field_id, value)`, `select_combobox(field_id, value)`, `click_button(button_id)`.
2. **Handling Complex Controls (e.g., Autocomplete, Dates)**
   - **Autocomplete**: If the LLM needs to fill an address, it should try typing part of it, extract the resulting dropdown options via Playwright, and choose the best match. (e.g., User: "МО, Луховицы, Пионерская" -> Agent types "Московская", selects "Московская область", types "Лухов", selects "г. Луховицы", etc.).
   - **Date/Time Slots**: If the user says "tomorrow evening", the agent parses the available slots rendered in the DOM, calculates "tomorrow", filters for "evening" times, and selects an available slot.
3. **Validation and Error Handling**
   - Check DOM for error messages after filling fields. Feed errors back to the LLM to ask the user for correction.

## Phase 5: Navigation and Completion
1. **Submitting the Screen**
   - Once the LLM determines all required fields are filled correctly, use Playwright to click the "Next" (submit) button.
2. **Handling Screen Transitions**
   - Detect when the page navigates or the DOM significantly changes (indicating the next screen loaded).
   - Loop back to Phase 2 (Extract HTML) for the new screen.
3. **Completion State**
   - Detect the final success screen and notify the user that the process is complete.

## Phase 6: Refinement
1. **Robustness**
   - Add explicit waits for dynamic content loading (e.g., waiting for autocomplete options to appear).
2. **Agent Logging**
   - Log LLM reasoning, DOM interactions, and extracted state for debugging.
