# Agent Development Plan (SSR & LLM Integration)

This document outlines the step-by-step development process for the Python agent script. The agent acts as a user, interacting with the frontend via SSR (Server-Side Rendering) and using an LLM to converse with the actual user to gather required information and fill out the screens.

**Note: The use of browser automation libraries (like Playwright, Selenium, Puppeteer) is strictly forbidden.** The agent must operate via standard HTTP clients interacting with an Angular SSR backend.

## Completed Phases (1-56)
- **Phases 1-56:** Core functionality including agent loop, SSR parsing, tools, state management, JS execution, mock implementations for endpoints (auth, analytics, webhooks, cache, settings, profile, feature flags, notifications, comments, audit logs, file uploads, weather, subscriptions, events, payments, support tickets, user tasks, devices, emails, orders, invoices, products), and system search via `/api/search`.

## Planned Features
- [x] **Phase 57:** Implement background task management endpoints (`/api/tasks`) support in the Python agent to start tasks and get their status.
- [x] **Phase 58:** Implement generic CRUD resource management endpoints (`/api/resource`) support in the Python agent to list, get, create, update, and delete resources.
