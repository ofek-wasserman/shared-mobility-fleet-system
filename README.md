# Vehicle Sharing API — Advanced Programming Final Project

A backend system for a vehicle-sharing service, implementing ride lifecycle management including user registration, ride handling, vehicle allocation, and maintenance flows.

## Tech Stack
- Python 3.12
- FastAPI
- Pytest
- GitHub Actions (CI)
- Jira for planning and traceability

## Repository Structure
- src/        → application code
- tests/      → test suite
- data/       → input CSV files (stations, vehicles)
- docs/       → documentation
- .github/    → CI configuration

## Local Setup

Create virtual environment:
    python3.12 -m venv .venv
    source .venv/bin/activate

Install dependencies:
    python -m pip install -r requirements.txt

Run tests:
    python -m pytest -q

Run server:
    uvicorn src.main:app --reload

## API Usage Examples

Start server, then:

Register user:
    POST /register

Start ride:
    POST /ride/start

End ride:
    POST /ride/end

## Supported Features

The system supports the following core functionalities:

- User registration with unique payment token
- Starting a ride with deterministic vehicle selection
- Ending a ride with automatic station selection and billing
- Reporting a vehicle as degraded during a ride
- Vehicle treatment and reintegration into stations
- Retrieval of nearest station based on location
- Retrieval of currently active users

The API uses structured error handling with appropriate HTTP status codes (400, 404, 409).

## Architecture

The system follows a layered architecture:

- API Layer  
  Handles HTTP requests, validation, and response mapping using FastAPI.

- Service Layer  
  Contains business logic and orchestrates workflows such as ride start/end, pricing, and vehicle treatment.

- Domain Layer  
  Defines core entities (Vehicle, Ride, User, Station) and enforces invariants.

- Data Layer  
  Responsible for CSV loading and state persistence (state.json).


## Workflow

Branch per Jira ticket:
    feature/KAN-XX-description

PR to main requires:
- 1 approval
- CI passing
- branch up to date

Definition of IN REVIEW:
- PR opened
- CI running or green

Definition of DONE:
- PR merged to main
- CI green on main