# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-8)
- **Phases 1-8:** Project setup, HTTP client, SSR HTML parsing (including dialogs and file uploads), LLM chat loop integration, form validation/submission, and advanced tools like downloading and parsing files are implemented.

## Phase 9: LLM Resilience
- [x] 1. Add retry logic for LLM API calls to handle transient errors.
- [x] 2. Implement timeout handling for long-running LLM queries.

## Phase 10: Usage Tracking
- [ ] 1. Implement token usage tracking.
