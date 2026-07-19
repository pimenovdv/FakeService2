# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-25)
- **Phases 1-25:** Implemented HTTP client, SSR HTML parsing, LLM chat loop, form validation, download/upload tools, resilience, token tracking, custom prompts, state persistence, form abort/handoff/pause, chat export, reset session, stats, preferences, retrieve available services tools, generate mock data tool, `get_system_health` tool, `get_weather` tool, and `get_exchange_rate` tool.

## Phase 26: Additional Utility Tools
- [x] 1. Implement `translate_text` tool to mock translate text from one language to another.
- [x] 2. Implement `calculate_distance` tool to mock calculate distance between two locations.

## Phase 27: Frontend JavaScript Logic Handling
- [ ] 1. Enhance the HTTP client and HTML parsing logic to detect and extract embedded `<script>` blocks or inline event handlers from the frontend SSR response.
- [ ] 2. Update LLM prompts to instruct the model to analyze and reason about the extracted JavaScript logic, simulating client-side behavior without a real browser.
- [ ] 3. Implement tools or internal mechanisms within the agent to evaluate simple state changes dictated by the extracted frontend JS logic.
