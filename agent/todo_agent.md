# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-20)
- **Phases 1-20:** Implemented project setup, HTTP client, SSR HTML parsing, LLM chat loop integration, form validation/submission, advanced tools (download/parse files, file upload), LLM resilience, token usage tracking, system prompt personalization via config, state persistence, form abortion tool, request human handoff tool, session pausing, chat history export, reset session tool, session stats tool, and user preferences tool.

## Phase 21: Retrieve Available Services Tool
- [x] 1. Implement `retrieve_available_services` tool in the agent, allowing the LLM to query and list available service IDs from the backend.

## Phase 22: Generate Mock Data Tool
- [ ] 1. Implement `generate_mock_data` tool to auto-generate mock values for the current form to help the user fill it out faster.