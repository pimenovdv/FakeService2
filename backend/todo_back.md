# Backend Development Plan (FastAPI Mock Server)

This document outlines the step-by-step development process for the FastAPI-based mock backend.

## Completed Phases
- **Phases 1-6:** Project setup, data models, core endpoints, scenarios, configuration-based routing, and extensive tests (unit and API tests).
- **Phase 7:** Enhanced Scenario Engine:
  - [x] **Configuration-driven Routing**
  - [x] **Support for 'Previous Step'**

## Phase 8: Data Collection and Output
1. [ ] **Store User Journey Data**
   - Implement temporary state storage (e.g., in-memory store) to track complete journeys before saving.
2. [ ] **Final Submission Endpoint**
   - Create an endpoint triggered at the end of the scenario that saves the collected data into a unified JSON format or mock database.
