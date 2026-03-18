# Project Folder Structure (Source of Truth)

This document defines the agreed repository layout.
If the structure changes, update this file in the same PR.

---

## High-level layout

project/
├─ src/                          # Application source code
│  ├─ __init__.py
│  ├─ main.py                    # FastAPI app factory and startup configuration
│  ├─ bootstrap.py               # Application bootstrap from CSV + persisted state
│  ├─ api/                       # FastAPI routes, schemas, dependencies, error handling
│  ├─ services/                  # Business logic orchestration
│  ├─ domain/                    # Core domain entities and invariants
│  └─ data/                      # CSV loaders and persistence helpers
│
├─ tests/                        # All tests (mirrors src/ structure where applicable)
│  ├─ conftest.py                # Shared pytest fixtures and test setup
│  ├─ test_smoke.py              # Basic import/bootstrap sanity test
│  ├─ test_bootstrap.py          # Bootstrap and startup-related tests
│  ├─ test_e2e.py                # End-to-end API flow tests
│  ├─ api/                       # API-level tests
│  ├─ services/                  # Service-layer tests
│  ├─ domain/                    # Domain model tests
│  └─ data/                      # Data/persistence tests
│
├─ data/                         # Initial CSV files used to bootstrap the application
│  ├─ stations.csv
│  └─ vehicles.csv
│
├─ docs/                         # Project documentation
│  ├─ DECISIONS.md
│  ├─ FOLDER_STRUCTURE.md
│  └─ WORKFLOW_and_GUIDELINES.md
│
├─ .github/
│  ├─ workflows/ci.yml           # CI pipeline (lint + tests)
│  └─ PULL_REQUEST_TEMPLATE.md
│
├─ requirements.txt              # Python dependencies
├─ pyproject.toml                # Tooling/configuration
├─ pytest.ini                    # Pytest configuration
├─ uv.lock                       # Locked dependency resolution
├─ .gitignore
└─ README.md

> Notes:
> - `tests/` mirrors the `src/` layer structure where relevant.
> - `data/` contains the real CSV files used to bootstrap the application.
> - Runtime-generated files such as `state.json` must not be committed to the repository.

---

## Layer responsibilities

### `src/domain/`
Pure domain logic:
- Entities (`Vehicle`, `Ride`, `User`, `Station`)
- Enums
- Invariants and validation rules

Contains no I/O, no FastAPI code, and no CSV access.

### `src/services/`
Business orchestration:
- `FleetManager`
- `ActiveRidesRegistry`
- `BillingService`
- Ride lifecycle logic
- Deterministic selection rules

Uses domain objects, but does not know about HTTP or FastAPI.

### `src/api/`
FastAPI layer:
- App wiring support
- Route definitions
- Request/response schemas
- Dependency injection (e.g., `get_fleet_manager`)
- HTTP error mapping

Translates HTTP requests into service calls and maps service/domain errors into HTTP responses.

### `src/data/`
Infrastructure layer:
- CSV loading
- Persistence helpers
- Runtime state serialization/restoration

Contains no business logic.

### `src/bootstrap.py`
Application bootstrap logic:
- Loads base data from CSV
- Builds the `FleetManager`
- Restores persisted runtime state if available

### `src/main.py`
Application entry point:
- Creates the FastAPI app
- Registers routers and exception handlers
- Configures startup/lifespan behavior

---

## Testing structure

The `tests/` directory is organized by layer and by cross-cutting test scope.

### Domain tests (`tests/domain/`)
- Entity invariants
- State transitions
- Enum behavior

### Service tests (`tests/services/`)
- Ride lifecycle orchestration
- Deterministic vehicle selection
- Business rule validation

### Data tests (`tests/data/`)
- CSV parsing and validation
- Loader behavior
- Persistence snapshot save/load logic

### API tests (`tests/api/`)
- Request/response validation
- Error mapping (`400 / 404 / 409`)
- Endpoint behavior
- API integration tests

### Bootstrap tests (`tests/test_bootstrap.py`)
- Application bootstrap behavior
- Startup initialization
- CSV + persisted state interaction

### End-to-end tests (`tests/test_e2e.py`)
- Full request lifecycle through the FastAPI app
- Multi-step flows such as register → start ride → end ride

### Smoke test (`tests/test_smoke.py`)
- Minimal sanity test that imports work and the project boots correctly in CI.