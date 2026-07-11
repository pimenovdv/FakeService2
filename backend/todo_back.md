# Backend Development Plan (FastAPI Mock Server)

This document outlines the step-by-step development process for the FastAPI-based mock backend.

## Completed Phases (1-6)
- **Phase 1-3:** Project initialized with `uv`, core structure created. Data models (Pydantic) for screens, components, buttons, requests, and responses implemented. Core API endpoints (`/start`, `/next_step`) implemented.
- **Phase 4-5:** Mock JSON scenarios created. `ScenarioManager` implemented to serve scenarios and validate answers. Dynamic endpoints for components implemented.
- **Phase 6:** Unit and API tests written with `pytest` and `httpx`. All tests passing.

## Phase 7: Enhanced Scenario Engine
1. [x] **Configuration-driven Routing**
   - Replace hardcoded routing logic in `ScenarioManager` with a configuration-based mechanism (e.g., loading `service_1_routing.json` that maps state transitions).
2. [ ] **Support for 'Previous Step'**
   - Implement functionality to navigate back to the previous screen.
