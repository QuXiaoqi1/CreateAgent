# Plan 04: OpenFOAM Case Generator

## Goal

Generate runnable OpenFOAM cases from the confirmed CFD problem schema for the MVP standard cases: 2D straight pipe, 2D bent pipe, room ventilation, and flow around an object.

## Product Scope

This plan covers OpenFOAM directory generation, dictionary rendering, mesh configuration, solver configuration, and reproducible run scripts. It does not execute the solver.

## In Scope

- OpenFOAM case template system.
- `0/`, `constant/`, and `system/` generation.
- `blockMesh`-based geometry for simple cases.
- Solver and turbulence model dictionary rendering.
- Reproducible run scripts.
- Case metadata and generation manifest.

## Out of Scope

- Runtime environment detection.
- Solver execution.
- Advanced CAD import.
- `snappyHexMesh` for complex production CAD.
- ParaView automation.

## Key Decisions

- MVP should start with template-driven OpenFOAM cases.
- `blockMesh` is the default mesh route for supported simple geometry.
- The generator should fail loudly when the schema cannot be represented safely.
- Generated case files must be readable enough for advanced users to inspect.

## Supported OpenFOAM Routes

- `blockMesh` for simple 2D/2.5D geometry.
- `checkMesh` expected before solver execution.
- `simpleFoam` for steady incompressible turbulent flow.
- `icoFoam` for laminar transient cases where appropriate.
- `pisoFoam` or `pimpleFoam` for simple transient incompressible cases.
- `postProcess` hooks for downstream result extraction.

## Functional Requirements

- Generate valid OpenFOAM case directories.
- Select and configure solver based on schema.
- Generate boundary conditions for inlet, outlet, wall, vents, symmetry, and object boundaries.
- Generate physical property dictionaries.
- Generate control, discretization, and solver settings.
- Generate mesh configuration for all MVP case families.
- Generate `run.sh` or equivalent reproducible command script.
- Record solver choice and generation rationale.

## Implementation Tasks

- [ ] 1. Define case template structure.
  - Establish templates for `0`, `constant`, `system`, scripts, and metadata.
  - _Requirement: PRD 9.3, PRD 11.4_

- [ ] 2. Implement solver strategy mapping.
  - Map schema physics to `simpleFoam`, `icoFoam`, `pisoFoam`, or `pimpleFoam`.
  - Record selection rationale.
  - _Requirement: PRD 9.2, PRD 12.3_

- [ ] 3. Implement straight pipe case generation.
  - Generate geometry, mesh, inlet, outlet, wall, and target metrics.
  - _Requirement: PRD 9.2_

- [ ] 4. Implement bent pipe case generation.
  - Generate simplified elbow geometry with supported dimensions.
  - Validate bend parameters before rendering.
  - _Requirement: PRD 9.2_

- [ ] 5. Implement room ventilation case generation.
  - Generate room domain, inlet vent, outlet vent, walls, and velocity/pressure fields.
  - _Requirement: PRD 9.2_

- [ ] 6. Implement flow around object case generation.
  - Generate external domain and simple obstacle geometry.
  - Support at least circle/cylinder or rectangle obstacle in 2D.
  - _Requirement: PRD 9.2_

- [ ] 7. Implement OpenFOAM dictionary rendering.
  - Render `controlDict`, `fvSchemes`, `fvSolution`, `transportProperties`, `turbulenceProperties`, and field files.
  - _Requirement: PRD 11.4_

- [ ] 8. Implement run script generation.
  - Include mesh generation, mesh check, solver, and post-processing commands.
  - Include environment notes for local OpenFOAM or Docker execution.
  - _Requirement: PRD 8, PRD 12.3_

- [ ] 9. Implement case generation validation.
  - Check required files exist and required dictionary keys are present.
  - Fail before execution when files are incomplete.
  - _Requirement: PRD 13.3_

## Acceptance Criteria

- When a confirmed straight pipe schema is provided, the generator shall create a runnable OpenFOAM case directory.
- When a confirmed bent pipe schema is provided, the generator shall create a simplified 2D bend case or return a blocking representation error.
- When a confirmed room ventilation schema is provided, the generator shall create a room domain with inlet and outlet boundaries.
- When a confirmed flow-around-object schema is provided, the generator shall create an external flow case with object boundary conditions.
- When a case is generated, the delivery files shall include solver rationale and a reproducible run script.

## Test Plan

- Snapshot test generated dictionaries for all four case families.
- Unit test solver strategy mapping.
- Unit test boundary condition generation.
- Unit test template rendering with missing values.
- Integration test generated case structure using mocked OpenFOAM validation.

## Dependencies

- Plan 03 for confirmed schema.
- Plan 05 for execution and environment handling.
- Plan 06 for report inputs.

## Done Definition

- All four MVP standard case families can produce deterministic OpenFOAM case folders from validated schemas, with no manual editing required before execution.
