# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases
- **Phases 1-34:** Core agent loop, SSR parsing, tools, state management, JS execution engine integration, file validation, mock auth, and comprehensive offline form validation (including cross-field logic like match and required_if) before submission.

## Planned Features
- [ ] **Phase 35:** Add support for grouping related form fields and handling grouped validations.
- [ ] **Phase 36:** Implement handling for dependent fields dynamically populated based on choices in other fields.
- [ ] **Phase 37:** Implement simulated error recovery from simulated backend API failures during submission.
