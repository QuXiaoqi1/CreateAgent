# Plan 03: CFD Problem Schema And Validation

## Goal

Define the canonical structured CFD problem schema that connects user intent, extracted inputs, assumptions, solver strategy, OpenFOAM case generation, execution, and reporting.

## Product Scope

This plan creates the shared contract used by every downstream module. It is the product's source of truth for what is being simulated and why.

## In Scope

- Canonical CFD problem schema.
- Supported physics scope.
- Required and optional fields.
- Unit and dimension validation.
- Assumption and default tracking.
- User confirmation model.
- Capability boundary checks.

## Out of Scope

- OpenFOAM file rendering.
- Solver execution.
- UI implementation.
- Report writing.

## Key Decisions

- The schema must be strict enough to prevent invalid case generation.
- Every value should carry provenance: user-provided, extracted, defaulted, inferred, or confirmed.
- The system must refuse automatic execution when the problem exceeds MVP physics scope.
- The schema should support all four standard case families from day one.

## Supported MVP Physics

- Single-phase flow.
- Incompressible flow.
- Steady or simple transient flow.
- 2D simulation domains.
- Laminar or common RANS turbulence.
- Simple thermal fields only as later enhancement.

## Core Schema Sections

- `task`: title, language, source inputs, timestamps.
- `simulationObjective`: user goal and target metrics.
- `caseFamily`: straight pipe, bent pipe, room ventilation, flow around object.
- `geometry`: dimensions, topology, boundaries, coordinate system.
- `fluid`: name, density, viscosity, temperature if needed.
- `physics`: incompressible/compressible, steady/transient, laminar/turbulent.
- `boundaryConditions`: inlet, outlet, wall, symmetry, object, vents.
- `initialConditions`: velocity, pressure, turbulence fields.
- `solverStrategy`: solver, turbulence model, mesh method, post-processing plan.
- `assumptions`: defaults, rationale, risk, approval status.
- `validation`: completeness, warnings, blocking errors.

## Functional Requirements

- Represent all inputs required to generate a supported OpenFOAM case.
- Validate completeness before case generation.
- Detect unsupported physics and request human review.
- Store assumptions and default values with user approval.
- Provide structured validation errors that local UI/CLI/Web can display.
- Preserve source evidence for values extracted from screenshots or tables.

## Implementation Tasks

- [ ] 1. Define schema types.
  - Model task, geometry, fluid, physics, boundary conditions, solver strategy, assumptions, and validation results.
  - _Requirement: PRD 9.1, PRD 11.1_

- [ ] 2. Define supported case-family requirements.
  - Encode required fields for straight pipe, bent pipe, room ventilation, and flow around object.
  - _Requirement: PRD 9.2_

- [ ] 3. Implement validation rules.
  - Validate units, required dimensions, boundary completeness, fluid properties, and target metrics.
  - _Requirement: PRD 13.2_

- [ ] 4. Implement assumption tracking.
  - Mark values as user-provided, extracted, inferred, defaulted, or confirmed.
  - Require approval for defaulted values that affect physics or geometry.
  - _Requirement: PRD 11.2, PRD 12.2_

- [ ] 5. Implement capability boundary checks.
  - Reject or pause unsupported requests such as multiphase flow, combustion, complex CAD, or ambiguous geometry.
  - _Requirement: PRD 4.3, PRD 12.2_

- [ ] 6. Implement serialization.
  - Save and load the schema as part of the task workspace.
  - Include schema snapshots in the final delivery package.
  - _Requirement: PRD 8, PRD 13.2_

## Acceptance Criteria

- When extracted inputs are incomplete, the schema validator shall return blocking validation errors with user-facing questions.
- When values are defaulted, the schema shall record the default, rationale, risk, and approval state.
- When the problem is outside the MVP physics scope, the system shall refuse automatic execution and recommend human review.
- When a problem is valid, the schema shall contain all information needed by the OpenFOAM case generator.
- When the delivery package is created, the schema snapshot shall be included for reproducibility.

## Test Plan

- Unit test validation for all four MVP case families.
- Unit test required/optional/default field behavior.
- Unit test unsupported physics rejection.
- Unit test serialization and deserialization.
- Integration test input draft to confirmed schema transition.

## Dependencies

- Plan 02 for extracted draft inputs.
- Plan 04 for case generation contract.
- Plan 06 for assumptions and report content.

## Done Definition

- No OpenFOAM case can be generated unless the confirmed CFD problem schema passes validation or explicitly enters a human-review path.
