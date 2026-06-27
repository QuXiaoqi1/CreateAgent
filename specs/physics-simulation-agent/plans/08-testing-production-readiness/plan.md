# Plan 08: Testing And Production Readiness

## Goal

Define and implement the production-grade MVP quality bar for the Physics Simulation Agent platform.

## Scope

This plan ties together tests, fixtures, golden cases, smoke tests, diagnostics, and release readiness.

## In Scope

- Golden cases.
- Unit tests.
- Integration tests.
- Mock full workflow.
- Conditional real OpenFOAM smoke test.
- Release readiness report.
- Known limitations and next-domain readiness.

## Out of Scope

- Full benchmark suite for all physics fields.
- Formal engineering certification.
- Cloud observability.
- Enterprise security program.

## Golden Cases

- CFD straight pipe.
- CFD bent pipe.
- CFD room ventilation.
- CFD flow around object.
- Non-MVP heat-transfer draft only.
- Non-MVP solid-mechanics draft only.

## Implementation Tasks

- [x] 1. Define fixture structure.
  - Include prompts, tables, schema snapshots, generated solver input, fixture logs, reports, and expected errors.
  - _Requirement: PRD 14_

- [x] 2. Add schema tests.
  - Cover generic schema, CFD extension, missing values, defaults, and unsupported domains.
  - _Requirement: PRD 13.2_

- [x] 3. Add intake tests.
  - Cover domain classification, table parsing, screenshot mock extraction, and clarification questions.
  - _Requirement: PRD 13.1_

- [x] 4. Add registry and adapter tests.
  - Cover OpenFOAM selection and unsupported future domain behavior.
  - _Requirement: PRD 13.3_

- [x] 5. Add CFD/OpenFOAM case generation tests.
  - Snapshot four MVP cases.
  - _Requirement: PRD 11.5_

- [x] 6. Add execution tests.
  - Mock local OpenFOAM, Docker fallback, command logging, and failures.
  - _Requirement: PRD 13.4_

- [x] 7. Add report and package tests.
  - Verify package completeness and report content.
  - _Requirement: PRD 13.5_

- [x] 8. Add end-to-end dry run.
  - Run one full mocked workflow from user input to delivery package.
  - _Requirement: PRD 10_

- [x] 9. Add conditional real smoke test.
  - If OpenFOAM or Docker is available, run a minimal straight-pipe case; otherwise skip gracefully.
  - _Requirement: PRD 11.6_

- [x] 10. Generate release readiness report.
  - List pass, fail, skip, known limitations, risks, and next recommended domain pack.
  - _Requirement: PRD 14_

## Acceptance Criteria

- When the test suite runs without OpenFOAM, mocked platform tests shall still pass.
- When OpenFOAM or Docker is available, a minimal real smoke test shall run or fail with actionable diagnostics.
- When a non-MVP domain is submitted, tests shall verify draft-only behavior without false solver support.
- When release readiness is generated, it shall state whether the MVP is production-ready and why.

## Implementation Evidence

- Added release-readiness checks in `physics-simulation-agent/physics_sim_agent/readiness.py`.
- Added non-MVP solid-mechanics draft fixture in `physics-simulation-agent/fixtures/solid_mechanics_draft.schema.json`.
- Upgraded Docker fallback execution path in `physics-simulation-agent/physics_sim_agent/execution.py`.
- Added readiness and Docker execution tests in `physics-simulation-agent/tests/test_readiness.py` and `physics-simulation-agent/tests/test_execution.py`.
- Generated readiness artifacts in `physics-simulation-agent/release-readiness/release-readiness.md` and `physics-simulation-agent/release-readiness/release-readiness.json`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 46 tests passed.
- Current readiness status: `ready_with_limitations` because local OpenFOAM and Docker are not available on this machine, so the real smoke test skipped gracefully.

## Test Plan

This file defines the cross-module test plan. Each module plan contributes its own tests.

## Done Definition

The platform has repeatable evidence for core behavior, known limitations, environment readiness, and MVP production quality.
