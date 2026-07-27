# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases
- **Phases 1-60:** Core functionality including agent loop, SSR parsing, tools, state management, JS execution, mock implementations for endpoints (auth, analytics, webhooks, cache, settings, profile, feature flags, notifications, comments, audit logs, file uploads, weather, subscriptions, events, payments, support tickets, user tasks, devices, emails, orders, invoices, products, background tasks, generic CRUD resources), system search via `/api/search`, `translate_text` refactoring, and `extract_document` tool for local file uploads to `/api/extract`.

## Planned Features
- [x] **Phase 61:** Add `manage_cart` tool (to interact with `/api/cart` endpoint) and `manage_reviews` tool (to interact with `/api/reviews` endpoint).
