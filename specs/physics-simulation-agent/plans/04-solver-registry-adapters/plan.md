# Plan 04: Solver Registry And Adapter Interfaces

## Goal

Create a solver registry and adapter interface so the platform can route validated physics problems to supported solvers without hard-coding one tool.

## Scope

This plan defines the platform's extension point for OpenFOAM now and FEniCSx, MOOSE, Chrono, or other solvers later.

## In Scope

- Solver adapter interface.
- Domain pack registration.
- Capability checks.
- Solver selection rationale.
- Adapter lifecycle hooks.
- OpenFOAMAdapter registration shell.

## Out of Scope

- Full FEniCSx/MOOSE/Chrono implementation.
- Solver-specific numerical templates except OpenFOAM shell integration.
- Execution engine internals.

## Adapter Responsibilities

- `canHandle(schema)`
- `explainCapability(schema)`
- `generateSolverInput(schema, workspace)`
- `getExecutionPlan(schema, workspace)`
- `parseLogs(logs)`
- `parseResults(results)`
- `describeLimitations()`

## Implementation Tasks

- [x] 1. Define domain pack metadata.
  - Include supported domains, case families, solvers, versions, limitations, and golden cases.
  - _Requirement: PRD 7.2_

- [x] 2. Define solver adapter interface.
  - Keep generation, execution planning, log parsing, result parsing, and limitations explicit.
  - _Requirement: PRD 7.3_

- [x] 3. Implement registry.
  - Register adapters and query candidates by physics domain and schema requirements.
  - _Requirement: PRD 11.4_

- [x] 4. Implement capability boundary result.
  - Return supported, unsupported, needs clarification, or human-review.
  - _Requirement: PRD 13.3_

- [x] 5. Add OpenFOAMAdapter registration shell.
  - Wire MVP CFD/OpenFOAM adapter into registry without implementing all case rendering here.
  - _Requirement: PRD 11.5_

- [x] 6. Add future adapter placeholders.
  - Document FEniCSx, MOOSE, and Chrono as future adapters with no false support claim.
  - _Requirement: PRD 12_

## Implementation Evidence

- Implemented adapter contracts and metadata in `physics-simulation-agent/physics_sim_agent/adapters.py`.
- Implemented registry selection in `physics-simulation-agent/physics_sim_agent/registry.py`.
- Added registry tests in `physics-simulation-agent/tests/test_registry.py`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 16 tests passed.

## Acceptance Criteria

- When a validated CFD/OpenFOAM schema is passed to the registry, the system shall select OpenFOAMAdapter.
- When a heat-transfer or solid-mechanics schema has no implemented adapter, the system shall return unsupported-but-structured status.
- When multiple adapters are possible, the system shall record selection rationale.
- When a request exceeds adapter capability, the system shall produce a user-readable limitation.

## Test Plan

- Unit test adapter registration.
- Unit test capability matching.
- Unit test unsupported domain result.
- Unit test solver selection rationale.

## Done Definition

The platform can add new physical simulation solvers by registering adapters instead of rewriting the workflow.
