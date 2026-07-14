# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-6)
- **Phases 1-6:** Project setup completed. HTTP client configured. SSR HTML extraction and parsing implemented. LLM integration with prompt engineering and interactive chat loop completed. Form interaction, simulated API actions, autocomplete handling, form validation/submission, and screen transitions are implemented. Robustness (graceful error handling) and agent logging (LLM reasoning and HTTP requests) have also been added.

## Phase 7: Advanced capabilities
- [ ] 1. Support multi-step modal dialogs.
- [ ] 2. Support file uploads.
