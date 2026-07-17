# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-18)
- **Phases 1-18:** Implemented project setup, HTTP client, SSR HTML parsing, LLM chat loop integration, form validation/submission, advanced tools (download/parse files, file upload), LLM resilience, token usage tracking, system prompt personalization via config, state persistence, form abortion tool, request human handoff tool, session pausing, chat history export, and reset session tool.

## Phase 19: Session Stats Tool
- [x] 1. Implement `get_session_stats` tool in the agent, allowing the LLM to retrieve current session token usage, message count, and other stats.

## Phase 20: User Preferences Tool
- [ ] 1. Implement `update_user_preferences` tool in the agent, allowing the LLM to store and update user preferences (e.g., tone, language) in the session state.