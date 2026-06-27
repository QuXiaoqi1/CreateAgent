# Plan 02: Physics Problem Schema

## Goal

Create the canonical Physics Problem Schema used by all domain packs and solver adapters.

## Scope

The schema represents the simulation problem, not any single solver's input format.

## In Scope

- Generic physics schema.
- Domain-specific extensions.
- Provenance and assumptions.
- Validation result model.
- Unit and dimension handling.
- Serialization.

## Out of Scope

- Solver input rendering.
- Numerical execution.
- UI implementation.

## Core Sections

- `simulationObjective`
- `physicsDomain`
- `governingModel`
- `geometry`
- `materials`
- `initialConditions`
- `boundaryConditions`
- `meshStrategy`
- `timeStrategy`
- `solverStrategy`
- `postprocessingTargets`
- `assumptions`
- `provenance`
- `validation`

## Implementation Tasks

- [x] 1. Define generic schema types.
  - Model objective, domain, geometry, materials, conditions, strategies, assumptions, and validation.
  - _Requirement: PRD 7.1_

- [x] 2. Define provenance model.
  - Track user-provided, extracted, table-derived, inferred, defaulted, and confirmed values.
  - _Requirement: PRD 8, PRD 13.1_

- [x] 3. Define assumption and approval model.
  - Store rationale, risk, default source, and approval status.
  - _Requirement: PRD 13.2_

- [x] 4. Define validation result model.
  - Support blocking errors, warnings, defaults, unsupported domain, and human-review states.
  - _Requirement: PRD 13.2_

- [x] 5. Implement domain extension hook.
  - Allow CFD/OpenFOAM and future heat/solid/PDE/multibody packs to extend schema safely.
  - _Requirement: PRD 7.2_

- [x] 6. Implement serialization.
  - Save `problem.schema.json` into every delivery package.
  - _Requirement: PRD 9_

## Implementation Evidence

- Implemented schema package under `physics-simulation-agent/physics_sim_agent/`.
- Added fixtures under `physics-simulation-agent/fixtures/`.
- Added unit tests under `physics-simulation-agent/tests/`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 8 tests passed.

## Acceptance Criteria

- When required values are missing, the schema validator shall return blocking questions.
- When a value is defaulted, the schema shall record rationale, risk, and approval state.
- When a domain pack extends the schema, generic platform fields shall remain stable.
- When a delivery package is generated, it shall include the confirmed schema snapshot.

## Test Plan

- Unit test valid generic schema.
- Unit test missing units and missing conditions.
- Unit test default approval flow.
- Unit test domain extension round trip.
- Snapshot test serialized schema.

## Done Definition

Every downstream module can rely on one schema contract instead of reading raw user input directly.
