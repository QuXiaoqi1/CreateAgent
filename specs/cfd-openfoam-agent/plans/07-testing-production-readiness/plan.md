# Plan 07: Testing And Production Readiness

## Goal

Make the CFD OpenFOAM Agent reliable enough for production-style use by adding test coverage, validation gates, reproducibility checks, environment diagnostics, and release readiness criteria.

## Product Scope

This plan cuts across all modules and defines the quality bar for calling the system production-grade.

## In Scope

- Unit test strategy.
- Integration test strategy.
- Golden standard cases.
- OpenFOAM case validation.
- Execution fallback validation.
- Report/package reproducibility checks.
- Error handling and diagnostics.
- Release checklist.

## Out of Scope

- Formal numerical validation against all CFD benchmarks.
- Certification-grade engineering validation.
- Large-scale cloud observability.
- Team security and permissions.

## Key Decisions

- Production-grade means stable, diagnosable, reproducible, and test-covered.
- Test fixtures should include the four MVP standard cases.
- Every failure path should be visible and actionable.
- Numerical results should be sanity-checked, not over-claimed.

## Quality Requirements

- Core schema validation is tested.
- Case generation is deterministic.
- Generated OpenFOAM folders pass structural checks before execution.
- Execution logs are never discarded.
- Environment selection is recorded.
- Delivery package can reproduce the run.
- Report includes assumptions and limitations.

## Golden Cases

- 2D straight pipe with known inlet velocity and pressure outlet.
- 2D bent pipe with known bend geometry.
- Room ventilation with inlet and outlet vents.
- Flow around a simple cylinder or rectangular obstacle.

## Implementation Tasks

- [ ] 1. Define test fixture structure.
  - Store input prompts, tables, expected schema, generated case snapshots, fixture logs, and expected report snapshots.
  - _Requirement: PRD 13.3_

- [ ] 2. Add schema validation tests.
  - Cover valid, incomplete, ambiguous, and unsupported physics requests.
  - _Requirement: PRD 12.2, PRD 13.3_

- [ ] 3. Add input parsing tests.
  - Cover natural language, CSV/XLSX, pasted table text, and mocked screenshot extraction.
  - _Requirement: PRD 12.1, PRD 13.3_

- [ ] 4. Add case generation tests.
  - Snapshot generated dictionaries for all four golden cases.
  - Verify required OpenFOAM files exist.
  - _Requirement: PRD 12.3, PRD 13.3_

- [ ] 5. Add execution engine tests.
  - Mock local OpenFOAM and Docker fallback.
  - Test command logs, stage transitions, and failure diagnosis.
  - _Requirement: PRD 12.4, PRD 13.1_

- [ ] 6. Add report and package tests.
  - Snapshot reports.
  - Verify package contents and metadata completeness.
  - _Requirement: PRD 12.5, PRD 13.3_

- [ ] 7. Add end-to-end dry run.
  - Run a mocked full workflow from user input to delivery package.
  - Include at least one success path and one failure path.
  - _Requirement: PRD 10_

- [ ] 8. Add real OpenFOAM smoke test when environment is available.
  - If local OpenFOAM or Docker is available, run one minimal straight-pipe case.
  - Skip gracefully when neither environment is available.
  - _Requirement: PRD 6.1, PRD 13.1_

- [ ] 9. Define release readiness checklist.
  - Include test pass status, environment checks, fixture coverage, known limitations, and packaging status.
  - _Requirement: PRD 5, PRD 13_

## Acceptance Criteria

- When tests run in an environment without OpenFOAM, the mocked test suite shall still validate parsing, schema, generation, logging, and report behavior.
- When local OpenFOAM or Docker is available, the smoke test shall execute one generated case or report a clear environment failure.
- When a generated case is incomplete, tests shall fail before solver execution.
- When a failure fixture is processed, the system shall produce a structured diagnosis.
- When release readiness is checked, the system shall report pass/fail status for every production-grade requirement.

## Test Plan

- This file is itself the test plan for the whole product.
- Each module plan should contribute unit and integration tests.
- The release checklist should be run before creating `consolidation.md`.

## Dependencies

- All other plans.

## Done Definition

- The project has repeatable tests, golden fixtures, environment diagnostics, and release checks that support the claim of a production-grade MVP.
