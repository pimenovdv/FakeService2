# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-30)
- **Phases 1-29:** Core agent loop, SSR parsing, tools, state, and context capabilities completed.
- [x] **Phase 30:** Implement a real JS execution engine (e.g., PyMiniRacer or PyV8) to make the `evaluate_js` tool non-mock, allowing the agent to evaluate actual frontend JavaScript logic instead of relying on mocks.
- [ ] **Phase 31:** Implement offline form validation logic evaluation before submission.
