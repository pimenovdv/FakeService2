# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Phase 1: Project Setup and Environment
- [x] 1. **Initialize Project**
   - Create a virtual environment (`uv` or `venv`).
   - Install dependencies: `httpx` (or `requests`) for HTTP communication, `langchain` (or preferred LLM library), `openai` (or specific LLM provider SDK), `beautifulsoup4` (for HTML parsing).
- [x] 2. **Configure HTTP Client**
   - Create a robust HTTP client session capable of managing cookies and headers, simulating a real user session hitting the Angular SSR endpoint (e.g., `http://localhost:4200/{service_id}/1`).

## Phase 2: SSR HTML Extraction and State Management
- [ ] 1. **Fetch Pre-rendered HTML**
   - Make an HTTP GET request to the Angular SSR endpoint.
   - Extract the fully rendered HTML response.
- [ ] 2. **Parse HTML Context**
   - Use `BeautifulSoup` to parse the HTML and identify input fields, labels, comboboxes, buttons, and validation rules present in the DOM (represented in the raw HTML).
   - Build a structured representation of the current screen's requirements (what fields need to be filled).

## Phase 3: LLM Integration and Conversation Loop
- [ ] 1. **Prompt Engineering**
   - Design system prompts for the LLM to understand its role: "You are an agent helping a user fill out a form. The form requires the following fields: {parsed_fields}. Ask the user for this information, use autocomplete features when available, and determine the values to input."
- [ ] 2. **Interactive Chat Loop**
   - Implement a CLI or simple API chat interface for the user.
   - Send the current form state and user input to the LLM.
   - The LLM should decide whether to ask the user a clarifying question or to execute actions to gather data or submit the form.

## Phase 4: Form Interaction and Autocomplete Handling
- [ ] 1. **Simulating Actions via API**
   - Create Python functions that the LLM can call (function calling/tools) to simulate interactions by making appropriate API calls that the frontend would normally make (e.g., `fetch_autocomplete_options(field_id, query)` or `simulate_form_submission(payload)`).
- [ ] 2. **Handling Complex Controls (e.g., Autocomplete, Dates)**
   - **Autocomplete**: If the LLM needs to fill an address, it must call the backend API endpoint (extracted from the HTML/JSON definitions) that the frontend autocomplete field uses, fetch the options, and match the user's input (e.g., User: "МО, Луховицы, Пионерская" -> Agent queries the API for "Московская", matches the result, queries for "Лухов", etc.).
   - **Date/Time Slots**: The agent parses the available slots rendered in the static HTML (or fetched via an API call mimicking the frontend), calculates required offsets (e.g., "tomorrow"), filters times, and selects an available slot ID.

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
