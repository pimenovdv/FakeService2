# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases
- **Phases 1-64:** Core functionality, state management, basic API integrations, manage_auth tool, stream_events tool.

## Planned Features
- [x] **Phase 65:** Implement `connect_websocket` tool to interact with websocket endpoints.
