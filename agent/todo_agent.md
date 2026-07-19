# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-26)
- **Phases 1-26:** Implemented HTTP client, SSR HTML parsing, LLM chat loop, form validation, download/upload tools, resilience, token tracking, custom prompts, state persistence, form abort/handoff/pause, chat export, reset session, stats, preferences, retrieve available services tools, generate mock data tool, `get_system_health` tool, `get_weather` tool, `get_exchange_rate` tool, `translate_text` tool, and `calculate_distance` tool.

## Phase 27: Frontend JavaScript Logic Handling
- [x] 1. Enhance the HTTP client and HTML parsing logic to detect and extract embedded `<script>` blocks or inline event handlers from the frontend SSR response.
- [x] 2. Update LLM prompts to instruct the model to analyze and reason about the extracted JavaScript logic, simulating client-side behavior without a real browser.
- [x] 3. Implement tools or internal mechanisms within the agent to evaluate simple state changes dictated by the extracted frontend JS logic.

## Phase 28: Multi-turn Tool Calling Execution
- [ ] 1. Implement support for chaining multiple tool calls within a single conversational turn (e.g. LLM decides to translate text then evaluate a JS script before replying to the user).
- [ ] 2. Add integration tests verifying the agent can handle sequential recursive tool calling gracefully.
