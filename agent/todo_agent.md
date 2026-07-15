# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-11)
- **Phases 1-11:** Project setup, HTTP client, SSR HTML parsing, LLM chat loop integration, form validation/submission, advanced tools (download/parse files), LLM resilience, token usage tracking, and system prompt personalization via config are all implemented.

## Phase 12: State Persistence
- [x] 1. Implement `save_state` and `load_state` methods in `ChatSession` to allow persisting and resuming agent conversations to/from a JSON file.
