# AI Agent Instructions (AGENTS.md)

Welcome, AI Agent. This document provides core instructions for working on this repository, which contains three distinct but interacting projects.

## Project Structure Overview

This repository is split into three main components:

1.  **`frontend/`**: An Angular-based application acting as a dynamic "screen player". It renders UI components based on JSON definitions received from the backend.
2.  **`backend/`**: A Python FastAPI mock server (using `uv`). It serves the JSON screen definitions and handles form submissions (next steps) for the frontend.
3.  **`agent/`**: A Python script designed to interact with the frontend application using SSR (HTTP requests to a pre-rendered Angular Universal application) and an LLM. It acts as an automated user, filling out forms based on a natural language conversation with a real human user.

## Core Development Philosophy

**CRITICAL DIRECTIVE: The Separation of Concerns (The "Secret Agent" Rule)**

*   **Frontend and Backend must NOT be designed or modified specifically to accommodate the `agent`.**
*   The `agent` must interact with the frontend exactly as a human user would, relying solely on the rendered HTML, standard DOM interactions, and visual/accessibility cues present in a normal web application.
*   Do not add special `id`s, hidden metadata, or specific API endpoints to the frontend or backend just to make the agent's job easier. The agent is developed "in secret" from the perspective of the application code.

## Workflow and Task Management

When working on any of the projects, you must adhere to the following workflow:

1.  **Follow the TODOs**: Each project directory contains a specific Markdown file outlining its development phases (e.g., `frontend/todo_front.md`, `backend/todo_back.md`, `agent/todo_agent.md`).
2.  **Execute Step-by-Step**: Work through the phases logically. Complete the foundational steps before moving to complex features.
3.  **Document Implementation Details**: As you implement specific components or features described in the TODO lists, you *must* document how you implemented them.
    *   For example, if you implement the "Text Input Control" in the frontend, update `frontend/todo_front.md` (or a linked architecture doc) to describe the actual Angular component structure, inputs, and validation logic used.
4.  **Update TODOs**: If a task proves more complex than anticipated and requires breaking down, or if new necessary steps are discovered during implementation, you are authorized and encouraged to update the relevant `todo_*.md` file to reflect the new plan. Keep the TODOs accurate and reflective of the current state of work.

## Project-Specific Instructions

### Frontend (Angular)
*   Ensure strict typing for the JSON schemas defining the screens.
*   Focus on dynamic rendering capabilities. The UI must be entirely driven by the backend JSON.
*   Implement robust validation that blocks submission until all rules are satisfied.

### Backend (FastAPI + uv)
*   Use `uv` for all dependency management and virtual environment creation.
*   Define clear Pydantic models that match the frontend's expected JSON structure exactly.
*   Keep the mock data realistic to support testing complex scenarios (like dependent dropdowns).

### Agent (Python SSR + LLM)
*   Prioritize robust DOM interaction (waiting for elements, handling dynamic updates).
*   The LLM prompts must accurately instruct the model to parse the HTML context and make decisions on how to interact with standard web controls (comboboxes, date pickers, etc.).
*   Implement tool calling/function calling so the LLM can execute concrete actions (click, type, select) via HTTP API calls mimicking the frontend requests based on the user's conversational input.

## Continuous Integration
* GitHub Actions workflows are located in `.github/workflows/`. Ensure tests pass for the respective project when committing changes.

### Important Technical Constraint: No Browser Automation
**WARNING: The use of browser automation libraries in the agent is STRICTLY FORBIDDEN.**
This includes, but is not limited to:
*   Playwright
*   Selenium
*   Browser Use
*   Puppeteer

The agent must interact with the frontend by making standard HTTP requests (e.g., using `httpx` or `requests`) to the Angular SSR endpoint and parsing the returned HTML using tools like `BeautifulSoup` or `lxml`. It must not launch or control a real browser.
