# Plan 06: Execution Environment And Engine

## Goal

Run solver inputs through a platform execution engine that supports local OpenFOAM first and Docker/OpenFOAM fallback for the MVP, while staying adapter-ready for future solvers.

## Scope

This plan covers environment detection, command orchestration, logs, stage status, failures, and recovery.

## In Scope

- Environment detection.
- Execution mode selection.
- Command runner.
- Stage orchestration.
- Log capture.
- OpenFOAM-specific parser hooks.
- Recovery and rerun behavior.

## Out of Scope

- Forced system installation.
- Remote HPC queues.
- Production cloud deployment.
- GPU scheduling.

## Implementation Tasks

- [x] 1. Implement environment capability model.
  - Represent local commands, container commands, versions, availability, and limitations.
  - _Requirement: PRD 11.6_

- [x] 2. Implement OpenFOAM local detection.
  - Detect OpenFOAM commands and version when available.
  - _Requirement: PRD 13.4_

- [x] 3. Implement Docker/OpenFOAM fallback.
  - Detect Docker and configured image without forcing installation.
  - _Requirement: PRD 3, PRD 13.4_

- [x] 4. Implement command runner.
  - Capture command, cwd, env summary, stdout, stderr, exit code, duration, and log paths.
  - _Requirement: PRD 14_

- [x] 5. Implement staged execution.
  - Run mesh generation, mesh check, solver, and post-processing according to adapter execution plan.
  - _Requirement: PRD 10_

- [x] 6. Implement OpenFOAM log parsing.
  - Parse `checkMesh`, residuals, convergence, missing files, boundary errors, floating point errors, and fatal errors.
  - _Requirement: PRD 13.4_

- [x] 7. Implement failure diagnosis.
  - Map common failures to probable causes and user-readable next actions.
  - _Requirement: PRD 9_

## Implementation Evidence

- Implemented execution engine in `physics-simulation-agent/physics_sim_agent/execution.py`.
- Wired OpenFOAMAdapter execution plan and log parsing.
- Added execution tests in `physics-simulation-agent/tests/test_execution.py`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 33 tests passed.

## Acceptance Criteria

- When compatible local OpenFOAM exists, the system shall select local mode and record version.
- When local OpenFOAM is missing and Docker is available, the system shall select Docker mode.
- When no execution environment is available, the system shall pause with clear setup guidance.
- When a command fails, raw logs and structured diagnosis shall be saved.
- When execution completes, stage status and logs shall be available for reporting.

## Test Plan

- Mock local command detection.
- Mock Docker fallback.
- Unit test command logging.
- Unit test OpenFOAM log parsers.
- Integration test mocked execution flow.
- Conditional real smoke test when OpenFOAM or Docker exists.

## Done Definition

The MVP can execute OpenFOAM cases reliably while the execution engine remains reusable for future solver adapters.
