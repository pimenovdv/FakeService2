# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-23)
- **Phases 1-23:** Implemented HTTP client, SSR HTML parsing, LLM chat loop, form validation, download/upload tools, resilience, token tracking, custom prompts, state persistence, form abort/handoff/pause, chat export, reset session, stats, preferences, retrieve available services tools, generate mock data tool, and `get_system_health` tool to retrieve current backend system status and connected services.

## Phase 24: Weather Tool
- [x] 1. Implement `get_weather` tool to retrieve mock weather data for a specified location.
