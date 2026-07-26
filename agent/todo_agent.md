# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-53)
- **Phases 1-53:** Core functionality including agent loop, SSR parsing, tools, state management, JS execution, mock implementations for endpoints (auth, analytics, webhooks, cache, settings, profile, feature flags, notifications, comments, audit logs, file uploads, weather, subscriptions, events, payments, support tickets, user tasks, devices, emails), and system search via `/api/search`.

## Planned Features
- [x] **Phase 54:** Implement order management endpoints (`/api/orders`) support in the Python agent to create, list, and get orders.
- [x] **Phase 55:** Implement invoice management endpoints (`/api/invoices`) support in the Python agent to create, list, get, and pay invoices.
- [x] **Phase 56:** Implement product management endpoints (`/api/products`) support in the Python agent to create, list, get, update, and delete products.
