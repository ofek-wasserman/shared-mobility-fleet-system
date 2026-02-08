# Vehicle Sharing API

Async REST backend for a vehicle sharing system (bikes, e-bikes, scooters).

## Quick Start

```bash
# Clone and checkout your branch
git clone <repo-url>
git checkout feature/role<N>-<your-role>

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest -q
```

## Project Structure

```
src/
  domain/      # Role 4: Entities, enums
  services/    # Role 3: FleetManager, BillingService
  api/         # Role 2: FastAPI endpoints
  data/        # Role 5: CSV loaders, persistence
tests/         # All test files
data/          # CSV files (stations.csv, vehicles.csv)
docs/          # Documentation
```

## Team Branches

| Branch | Role | Start |
|--------|------|-------|
| feature/role1-repo-ci | Repo/CI (Ariel) | Done |
| feature/role2-api | API Owner | Now |
| feature/role3-services | Core Services | Now |
| feature/role4-domain | Domain Model | Next week |
| feature/role5-data-persistence | Data/Persistence | Next week |

## Workflow

1. Work on your feature branch
2. Open PR to main when ready
3. CI must pass + 1 reviewer approval
4. Merge to main

## For Each Role

**Role 2 (API)**: Start with `src/api/main.py`, create FastAPI app and endpoints.

**Role 3 (Services)**: Start with `src/services/fleet_manager.py`, implement FleetManager.

**Role 4 (Domain)**: Start with `src/domain/enums.py` and `entities.py`.

**Role 5 (Data)**: Start with `src/data/loaders.py` for CSV loading.

See `docs/KICKOFF_PLAN.md` for full details.
