# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Features
- Project setup, SSR HTML extraction, parser, HTTP client.
- LLM integration with prompt engineering, interactive chat loop.
- Simulating Actions via API (form interactions)
- Form Validation and Submission to `/next_step`.
- Screen Transitions and Completion State handling.
- Agent Logging (LLM reasoning, HTTP requests/responses).

## Phase 4: Form Interaction and Autocomplete Handling
- [ ] 2. **Handling Complex Controls (e.g., Autocomplete, Dates)**
   - **Autocomplete**: If the LLM needs to fill an address, it must call the backend API endpoint (extracted from the HTML/JSON definitions) that the frontend autocomplete field uses, fetch the options, and match the user's input (e.g., User: "МО, Луховицы, Пионерская" -> Agent queries the API for "Московская", matches the result, queries for "Лухов", etc.).
   - **Date/Time Slots**: The agent parses the available slots rendered in the static HTML (or fetched via an API call mimicking the frontend), calculates required offsets (e.g., "tomorrow"), filters times, and selects an available slot ID.

## Phase 6: Refinement
- [ ] 1. **Robustness**
   - Handle HTTP errors, parsing errors, and malformed HTML gracefully.
- [x] 2. **Agent Logging**
   - Log LLM reasoning, HTTP requests/responses, and extracted state for debugging.
