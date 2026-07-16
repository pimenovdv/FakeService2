# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-14)
- **Phases 1-14:** Project setup, HTTP client, SSR HTML parsing, LLM chat loop integration, form validation/submission, advanced tools (download/parse files, file upload), LLM resilience, token usage tracking, system prompt personalization via config, state persistence, and form abortion tool are all implemented.

## Phase 15: Human Handoff Escalation
- [x] 1. Implement `request_human_handoff` tool in the agent, allowing the LLM to explicitly escalate the session to a human operator, providing a summary of the situation.
