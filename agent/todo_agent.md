# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-10)
- **Phases 1-10:** Project setup, HTTP client, SSR HTML parsing (including dialogs and file uploads), LLM chat loop integration, form validation/submission, advanced tools (downloading/parsing files), LLM resilience (retry logic, timeout handling), and token usage tracking are implemented.

## Phase 11: System Prompt Personalization
- [x] 1. Add ability to load system prompts from a configuration file to personalize the agent behavior per service.
