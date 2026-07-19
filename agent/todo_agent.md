# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-29)
- **Phases 1-29:** Implemented HTTP client, SSR HTML parsing, LLM chat loop, multi-turn tool execution, form validation/abort/handoff, JS logic evaluation, state persistence, token tracking, stats, preferences, and several basic tools (`get_system_health`, `get_weather`, `get_exchange_rate`, `translate_text`, `calculate_distance`, `get_current_datetime`, `generate_uuid`).

## Current Phase
- [x] **Phase 30:** Implement `search_web` and `summarize_text` tools.
