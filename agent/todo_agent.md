# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-31)
- **Phases 1-31:** Core agent loop, SSR parsing, tools, state management, JS execution engine integration, and offline form validation logic evaluation before submission.

## Planned Features
- [x] **Phase 32:** Implement file size and type validation logic for mock uploads.
- [ ] **Phase 33:** Add simulated mock authentication token management to AgentClient.
- [ ] **Phase 34:** Enhance offline form validation to support cross-field evaluations (e.g., match, required_if).
