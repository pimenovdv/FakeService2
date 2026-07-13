# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-3)
- **Phase 1-3:** Project setup completed. HTTP client configured. SSR HTML extraction and parsing implemented. LLM integration with prompt engineering and interactive chat loop completed.

## Phase 4: Form Interaction and Autocomplete Handling
- [x] Phase 4 complete: Simulated API actions and handling of complex controls (autocomplete, dates) implemented.

## Phase 5: Validation and Submission
- [ ] 1. **Submitting the Screen**
   - Once the LLM determines all required fields are filled correctly, construct the HTTP POST request representing the form submission (`/next_step`).
   - Include all necessary headers, cookies, and the `answers` JSON payload exactly as the frontend would.
- [ ] 2. **Handling Screen Transitions**
   - Analyze the response from the submission (which could be new HTML or a redirect to the next screen URL).
   - Loop back to Phase 2 (Fetch HTML) for the new screen.
- [ ] 3. **Completion State**
   - Detect the final success screen (by analyzing the resulting HTML or redirect URL) and notify the user that the process is complete.

## Phase 6: Refinement
- [ ] 1. **Robustness**
   - Handle HTTP errors, parsing errors, and malformed HTML gracefully.
- [ ] 2. **Agent Logging**
   - Log LLM reasoning, HTTP requests/responses, and extracted state for debugging.
