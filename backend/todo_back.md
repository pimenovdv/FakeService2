# Backend Development Plan (FastAPI Mock Server)

This document outlines the step-by-step development process for the FastAPI-based mock backend, designed to drive the Angular screen player.

## Phase 1: Project Setup and Dependencies
1. **Initialize Project with `uv`**
   - Create a virtual environment and `pyproject.toml` using `uv`.
   - Install dependencies: `fastapi`, `uvicorn`, `pydantic`.
2. **Project Structure**
   - Setup directories for routers, models, services, and mock data (JSON files).
3. **Basic App Setup**
   - Create `main.py` with FastAPI initialization and basic CORS middleware to allow requests from the Angular frontend.

## Phase 2: Data Models (Pydantic)
1. **Define Screen Models**
   - Create Pydantic models reflecting the JSON structure expected by the frontend:
     - `ComponentDef` (base class and specific implementations for Text, ComboBox, etc.)
     - `ButtonDef`
     - `ScreenDef` (header, content, components, buttons)
2. **Define Request/Response Models**
   - `StartRequest` (contains `service_id`)
   - `NextStepRequest` (contains `service_id`, current screen ID, and `answers` dictionary)
   - `NextStepResponse` (returns the next `ScreenDef` or a completion payload)

## Phase 3: Core API Endpoints
1. **POST `/start` Endpoint**
   - Receives `service_id`.
   - Loads the initial screen definition for the given `service_id` from mock JSON files.
   - Returns the `ScreenDef`.
2. **POST `/next_step` Endpoint**
   - Receives answers from the frontend.
   - Validates the answers against expected types (basic validation).
   - Determines the next screen based on the `service_id` and provided answers (mock routing logic).
   - Returns the next `ScreenDef`.

## Phase 4: Mock Data Scenarios
1. **Create Mock JSON Scenarios**
   - Define a series of JSON files representing a sequence of screens for a specific `service_id` (e.g., `service_1_screen_1.json`, `service_1_screen_2.json`).
   - Include examples of dynamic dependencies (e.g., a screen that changes based on an answer from a previous screen).
2. **Implement Scenario Manager**
   - Create a service class to load and serve these JSON files based on the state or request parameters.

## Phase 5: Dynamic API Endpoints for Components
1. **Implement Dynamic Data Endpoints**
   - Create generic endpoints (e.g., `GET /api/data/{data_source}`) that components (like ComboBoxes) can call to fetch dynamic options.
   - Serve mock data for these endpoints based on the `data_source` parameter.

## Phase 6: Refinement and Testing
1. **Unit Tests**
   - Write tests for Pydantic models and basic routing logic.
2. **API Tests**
   - Use `pytest` and `httpx` to test `/start`, `/next_step`, and dynamic endpoints.
   - Ensure the server correctly handles invalid data and returns appropriate HTTP status codes.
