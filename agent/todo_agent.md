# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-45)
- **Phases 1-44:** Core functionality including agent loop, SSR parsing, tools, state management, JS execution, and mock implementations for auth, analytics, webhooks, cache, settings, profile, feature flags, notifications, comments, audit logs, and file uploads.
- **Phase 45:** Add functionality to perform system searches via the `/api/search` endpoint using the Python agent.

## Planned Features

- [ ] **Phase 46:** Add functionality to get weather for a city via the `/api/weather` endpoint using the Python agent.
