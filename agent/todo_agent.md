# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases
- **Phases 1-62:** Core functionality (agent loop, SSR parsing, JS eval, state management, basic API integrations).

## Planned Features
- [x] **Phase 63:** Implement `manage_auth` tool to interact with backend authentication endpoints (`login`, `me`, `token`, `authorize`, `admin-data`).
- [x] **Phase 64:** Implement `stream_events` tool to interact with `/api/stream` endpoint, reading SSE streams.
