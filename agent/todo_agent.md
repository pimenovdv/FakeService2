# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-29)
- **Phases 1-28:** Implemented HTTP client, SSR HTML parsing, LLM chat loop, multi-turn tool execution, form validation/abort/handoff, JS logic evaluation, state persistence, token tracking, stats, preferences, and several basic tools (`get_system_health`, `get_weather`, `get_exchange_rate`, `translate_text`, `calculate_distance`).
- [x] **Phase 29:** Implement `get_current_datetime` and `generate_uuid` tools to provide real-time environment context to the LLM.
- [ ] **Phase 30:** Implement a real JS execution engine (e.g., PyMiniRacer or PyV8) to make the `evaluate_js` tool non-mock, allowing the agent to evaluate actual frontend JavaScript logic instead of relying on mocks.
