# Plan 05: CFD OpenFOAM Domain Pack

## Goal

Implement the MVP `domain-pack-cfd-openfoam` that turns validated CFD schemas into runnable OpenFOAM cases for four standard case families.

## Scope

This plan preserves the original CFD/OpenFOAM MVP inside the broader Physics Simulation Agent platform.

## In Scope

- CFD schema extension.
- Four case-family validators.
- OpenFOAM solver strategy mapping.
- Template-driven case generation.
- `blockMesh` geometry generation for simple cases.
- Run script and metadata generation.

## Out of Scope

- Complex CAD import.
- Advanced `snappyHexMesh`.
- Combustion, chemical reactions, complex multiphase flow.
- High-fidelity validation against all benchmarks.

## Supported MVP Cases

- 2D straight pipe.
- 2D bent pipe.
- Room ventilation.
- Flow around an object.

## Implementation Tasks

- [x] 1. Define CFD schema extension.
  - Add incompressible flow, steady/transient, turbulence, fluid properties, and CFD boundary types.
  - _Requirement: PRD 3, PRD 11.5_

- [x] 2. Implement case-family validators.
  - Validate straight pipe, bent pipe, room ventilation, and flow around object completeness.
  - _Requirement: PRD 13.3_

- [x] 3. Implement OpenFOAM solver strategy.
  - Map schema to `simpleFoam`, `icoFoam`, `pisoFoam`, or `pimpleFoam` where appropriate.
  - _Requirement: PRD 11.5_

- [x] 4. Implement OpenFOAM case templates.
  - Generate `0/`, `constant/`, `system/`, field files, `blockMeshDict`, and dictionaries.
  - _Requirement: PRD 11.5_

- [x] 5. Implement case generators for four MVP cases.
  - Start with straight pipe, then bent pipe, room ventilation, and flow around object.
  - _Requirement: PRD 3_

- [x] 6. Implement generation manifest.
  - Record schema hash, domain pack, adapter, solver, assumptions, and generation rationale.
  - _Requirement: PRD 9_

## Implementation Evidence

- Implemented OpenFOAM case generation in `physics-simulation-agent/physics_sim_agent/openfoam_case.py`.
- Wired `OpenFOAMAdapter.generate_solver_input()` to the domain pack generator.
- Added four golden case fixtures in `physics-simulation-agent/fixtures/cfd_golden_cases.json`.
- Added case generation structure tests in `physics-simulation-agent/tests/test_openfoam_case.py`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 25 tests passed.

## Acceptance Criteria

- When a straight pipe schema is valid, OpenFOAMAdapter shall generate a runnable case directory.
- When a bent pipe, room ventilation, or flow-around-object schema is valid, the adapter shall generate a deterministic case or a clear blocking error.
- When geometry is ambiguous, the adapter shall not guess.
- When a case is generated, metadata shall record the solver strategy and source schema.

## Test Plan

- Snapshot test generated OpenFOAM files.
- Unit test solver strategy mapping.
- Unit test boundary condition rendering.
- Unit test unsupported CFD feature rejection.
- Integration test schema to case generation for four golden cases.

## Done Definition

CFD/OpenFOAM remains the first fully executable domain pack inside the broader physics simulation platform.
