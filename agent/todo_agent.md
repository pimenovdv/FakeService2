# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-36)
- **Phases 1-36:** Core agent loop, SSR parsing, tools, state management, JS execution engine, file validation, mock auth, comprehensive offline form validation, mock analytics, and mock webhooks integration retrieval.

## Planned Features

- [ ] **Phase 37:** Implement mock cache interaction (GET/POST/DELETE) for the agent using `/api/cache/{key}` endpoint.