# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-15)
- **Phases 1-15:** Implemented project setup, HTTP client, SSR HTML parsing, LLM chat loop integration, form validation/submission, advanced tools (download/parse files, file upload), LLM resilience, token usage tracking, system prompt personalization via config, state persistence, form abortion tool, and request human handoff tool.

## Phase 16: Session Pausing
- [x] 1. Implement `pause_session` tool in the agent, allowing the LLM to explicitly pause the current session with a reason, indicating that the session can be resumed later using the saved state.