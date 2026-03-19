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

Run the project locally with Python 3.12:

1. Create and activate a virtual environment:
    python3.12 -m venv .venv
    source .venv/bin/activate

2. Install dependencies:
    python -m pip install -r requirements.txt

3. Run tests:
    python -m pytest -q

4. Start the API server:
    uvicorn src.main:app --reload

5. Open the API in your browser:
    http://127.0.0.1:8000/docs

## API Usage

After starting the server, the main endpoints are available through the API documentation page (`/docs`).

Main endpoints:
- POST /register
- POST /ride/start
- POST /ride/end
- POST /vehicle/treat
- POST /vehicle/report-degraded
- GET /stations/nearest
- GET /rides/active-users

### Example Requests

Register a user:
POST /register
{
  "payment_token": "token_123"
}

Start a ride:
POST /ride/start
{
  "user_id": 1,
  "lat": 32.0853,
  "lon": 34.7818
}

## Notes

- Initial system data is loaded from the CSV files in the `data/` directory.
- Runtime state is persisted in `state.json`.

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