# Plan 05: Execution Environment And Engine

## Goal

Run generated OpenFOAM cases reliably by detecting a local OpenFOAM installation first and falling back to Docker/OpenFOAM when needed.

## Product Scope

This plan covers environment detection, execution orchestration, logging, stage status, failure diagnosis, and rerun behavior.

## In Scope

- Local OpenFOAM detection.
- OpenFOAM version capture.
- Docker/OpenFOAM fallback.
- Command execution wrapper.
- Stage-by-stage orchestration.
- Log capture and parsing.
- Failure diagnosis and recovery suggestions.
- Restart from recoverable stages.

## Out of Scope

- Cloud/HPC scheduler integration.
- GPU execution.
- Distributed parallel OpenFOAM runs.
- Advanced runtime optimization.

## Key Decisions

- Prefer user local OpenFOAM if compatible.
- Use Docker/OpenFOAM fallback when local OpenFOAM is missing or incompatible.
- Every command must be logged with command, working directory, exit code, duration, stdout, and stderr.
- Failures should be explained in user language while preserving raw logs for experts.

## Execution Stages

- Environment check.
- Mesh generation.
- Mesh quality check.
- Solver execution.
- Post-processing commands.
- Delivery artifact collection.

## Functional Requirements

- Detect whether OpenFOAM commands are available locally.
- Detect OpenFOAM version where possible.
- Detect whether Docker is available.
- Select local or Docker execution mode.
- Execute `blockMesh`, `checkMesh`, solver command, and `postProcess` steps.
- Capture logs for every step.
- Parse common OpenFOAM errors.
- Update task status after every stage.
- Allow rerun from failed or selected stage where safe.

## Implementation Tasks

- [ ] 1. Implement environment detection.
  - Check for local OpenFOAM command availability and version.
  - Check Docker availability and configured image.
  - _Requirement: PRD 6.1, PRD 13.1_

- [ ] 2. Implement execution mode selection.
  - Prefer local OpenFOAM when compatible.
  - Fall back to Docker/OpenFOAM when local execution is unavailable.
  - Record selected mode in metadata.
  - _Requirement: PRD 6.1, PRD 8_

- [ ] 3. Implement command runner.
  - Capture command, cwd, environment summary, stdout, stderr, exit code, and duration.
  - Write logs to task workspace.
  - _Requirement: PRD 11.5, PRD 12.4_

- [ ] 4. Implement stage orchestration.
  - Run mesh generation, mesh check, solver, and post-processing in order.
  - Update task state at every stage.
  - _Requirement: PRD 10, PRD 11.5_

- [ ] 5. Implement `checkMesh` parser.
  - Identify pass/fail status and critical mesh quality issues.
  - Summarize results in user-readable form.
  - _Requirement: PRD 12.4_

- [ ] 6. Implement solver log parser.
  - Extract residuals, time steps, convergence markers, floating point errors, missing file errors, and boundary condition errors.
  - _Requirement: PRD 9.4, PRD 11.6_

- [ ] 7. Implement failure diagnosis.
  - Map common failures to probable causes and recommended next actions.
  - Include raw log references.
  - _Requirement: PRD 9.4, PRD 12.4_

- [ ] 8. Implement rerun support.
  - Allow safe rerun after case regeneration, mesh regeneration, or solver failure.
  - Preserve previous logs.
  - _Requirement: PRD 13.1_

## Acceptance Criteria

- When compatible local OpenFOAM is installed, the system shall use local execution and record the detected version.
- When local OpenFOAM is unavailable and Docker is available, the system shall run through the configured Docker/OpenFOAM image.
- When an OpenFOAM command fails, the system shall capture command, exit code, relevant log excerpt, probable cause, and recommended next action.
- When `checkMesh` completes, the system shall summarize whether critical checks passed.
- When the solver completes, the system shall record convergence status and key monitored values.

## Test Plan

- Unit test environment detection with mocked command availability.
- Unit test Docker fallback selection.
- Unit test command runner log capture.
- Unit test `checkMesh` parser against fixture logs.
- Unit test solver parser against success and failure logs.
- Integration test full execution path with mocked OpenFOAM commands.

## Dependencies

- Plan 01 for task state.
- Plan 04 for generated case and scripts.
- Plan 06 for parsed results and report inputs.

## Done Definition

- A generated case can be executed through local OpenFOAM or Docker fallback, and every execution outcome is recorded, diagnosable, and visible to the user.
