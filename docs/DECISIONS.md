# Project Decisions (Source of Truth)

This file freezes technical decisions so the implementation stays consistent across the team.
If a rule affects correctness, it must appear here.

---

## IDs and Types

- station_id: int (from stations.csv, never regenerated)
- vehicle_id: str (from vehicles.csv, never regenerated)
- user_id: int (generated incrementally by the system)
- ride_id: int (generated incrementally by the system)

IDs are never reused.

---

## Deterministic Vehicle Selection

When starting a ride at the selected station:

- Choose the eligible vehicle with the smallest number of rides since last treatment.
- In case of a tie, choose the vehicle with the smallest ID.

No randomness is allowed anywhere in the system.

---

## Distance Calculation

- Use Euclidean distance on (latitude, longitude) for all "nearest station" logic.
- If tie occurs, choose station with smallest station_id.

---

## Pricing

Phase 1:

- Fixed price of 15 ILS per ride.

Future phases:

- Additional pricing rules (e.g., degraded handling) will be implemented in Phase 2.

Pricing logic lives strictly in the service layer.

---

## Error Mapping (Service → API)

400:
Invalid input (schema/type/validation)

404:
Entity not found (user/vehicle/station/ride missing)

409:
Invalid state transition
(e.g., user already has active ride,
no eligible vehicles,
destination station full)

Service layer raises domain/service errors.
API layer translates them into HTTP responses.

---

## Persistence Strategy

Phase 1:

- Load initial state from CSV on startup.
- No saving of mutable runtime state.

Phase 2:

- Save/load mutable runtime state
  (vehicle status, degraded state, active rides if required).
- Restart behavior must not corrupt state.

---

## state.json Schema (Phase 2)

The runtime state is persisted to `state.json` after every mutating operation
and loaded on startup when the file exists.

### What is stored

Only runtime-generated or mutable data:

- Registered users (generated at runtime, not in CSV)
- Active rides (in-progress, not persisted in CSV)
- Completed rides history (for audit/billing history)
- Mutable vehicle fields (status, rides_since_last_treated, last_treated_date, station_id)
- Degraded repository vehicle IDs

Static data (station coordinates, vehicle type, initial CSV values) is NOT
duplicated in state.json. It is always re-read from CSV on startup.

### Field reference

| Field              | Type              | Description                                                      |
|--------------------|-------------------|------------------------------------------------------------------|
| schema_version     | int               | Schema version, starts at 1. Increment on breaking changes.      |
| saved_at           | string (ISO 8601) | UTC timestamp of last save. For debugging only.                  |
| next_user_id       | int               | Next user_id to assign. Prevents collision across restarts.      |
| next_ride_id       | int               | Next ride_id to assign. Counts all rides, not just active.       |
| users              | object            | Map of user_id (string) → user object.                          |
| active_rides       | object            | Map of ride_id (string) → active ride object.                   |
| completed_rides    | array             | List of completed ride objects, ordered by ride_id ascending.    |
| vehicles           | object            | Map of vehicle_id (string) → mutable vehicle fields only.       |
| degraded_repo      | array             | Sorted list of vehicle_id strings currently in degraded repo.    |

### JSON structure

```json
{
  "schema_version": 1,
  "saved_at": "2026-03-09T12:00:00",
  "next_user_id": 5,
  "next_ride_id": 12,
  "users": {
    "1": {
      "user_id": 1,
      "payment_token": "tok_abc123"
    }
  },
  "active_rides": {
    "7": {
      "ride_id": 7,
      "user_id": 1,
      "vehicle_id": "V003",
      "start_time": "2026-03-09T11:45:00",
      "start_station_id": 2,
      "reported_degraded": false
    }
  },
  "completed_rides": [
    {
      "ride_id": 6,
      "user_id": 2,
      "vehicle_id": "V001",
      "start_time": "2026-03-09T10:00:00",
      "start_station_id": 1,
      "end_time": "2026-03-09T10:30:00",
      "end_station_id": 3,
      "reported_degraded": false,
      "price": 15.0
    }
  ],
  "vehicles": {
    "V001": {
      "status": "available",
      "rides_since_last_treated": 3,
      "last_treated_date": "2026-01-15",
      "station_id": 3
    },
    "V003": {
      "status": "available",
      "rides_since_last_treated": 1,
      "last_treated_date": "2026-02-01",
      "station_id": null
    }
  },
  "degraded_repo": ["V002", "V007"]
}
```

### Field-level rules

**Datetime values** (start_time, end_time, saved_at):
- ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
- Naive (no timezone suffix), consistent with `datetime.now()`

**Date values** (last_treated_date):
- ISO 8601 format: `YYYY-MM-DD`

**JSON object keys**:
- All ID-keyed maps use string keys (JSON requirement)
- Values carry the native typed field (e.g., `"user_id": 1` as int)

**vehicles.station_id**:
- Integer station_id if vehicle is docked
- `null` if vehicle is in an active ride or in the degraded repo

**degraded_repo**:
- Sorted lexicographically for deterministic output

**completed_rides**:
- Ordered by ride_id ascending for deterministic output

### Restoration procedure (Phase 2 bootstrap)

On startup, if `state.json` exists:

1. Load CSV (stations and vehicles) — provides static/base fields
2. Apply `vehicles` overrides — overwrite mutable fields for each vehicle_id
3. Restore `users` dict and `_registered_tokens` set
4. Restore `ActiveRidesRegistry` from `active_rides`
5. Restore completed rides history from `completed_rides`
6. Restore `DegradedRepo` from `degraded_repo`
7. Set ID counters to `next_user_id` and `next_ride_id`

If `state.json` does not exist, fall back to Phase 1 CSV-only bootstrap.

### Invariants that must hold after restore

- Every vehicle_id in `active_rides` must have `station_id: null` in `vehicles`
- Every vehicle_id in `degraded_repo` must not appear in any station inventory
- All vehicle_ids referenced must exist in the vehicles CSV
- All station_ids referenced must exist in the stations CSV
- `next_ride_id > max(active ride IDs ∪ completed ride IDs)`
- `next_user_id > max(user IDs)`

---

## Fleet Invariants (Phase 1)

The following invariants must always hold during runtime.

---

## Vehicle Eligibility (Phase 1)

A vehicle is considered eligible (rentable) if:

- status == AVAILABLE
- active_ride_id is None
- rides_since_last_treated <= 10

Vehicle degradation rules:

- A vehicle becomes unrentable (degraded) if:
  - rides_since_last_treated > 10, or
  - a user reports it as degraded

Maintenance / treatment rules:

- Treatment may be initiated only on:
  - degraded vehicles, or
  - vehicles with rides_since_last_treated >= 7

Eligibility rules may expand in Phase 2, but the concept of eligibility remains centralized in the service layer.

---

## Station Membership Invariant

Regular stations must contain only eligible vehicles.

Vehicles that are not eligible must not remain in regular stations.

Specifically:

- Vehicles currently in ride belong to the Active Rides registry.
- Vehicles reported as degraded belong to the Degraded Repository.
- Vehicles with rides_since_last_treated > 10 belong to the Degraded Repository.

---

## Bootstrap Normalization Rule

On system startup (after CSV bootstrap):

FleetManager must validate all loaded vehicles and normalize system state:

- Ineligible vehicles must be removed from regular stations.
- Ineligible vehicles must be placed in the appropriate repository.
- Regular stations must end initialization containing only eligible vehicles.

This invariant must be maintained on every state transition
(start ride, end ride, maintenance handling).
