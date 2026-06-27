# Plan 01: Platform Product Shell

## Goal

Build the local-first product shell for Physics Simulation Agent, with task workspace, state management, artifact registry, user checkpoints, and adapter-ready workflow boundaries.

## Scope

This plan covers the product shell shared by every physics domain. It does not implement a solver or domain-specific case generation.

## In Scope

- Local task workspace.
- Task status model.
- Input artifact registration.
- User confirmation checkpoints.
- Artifact registry.
- Workflow controller boundaries.
- Future CLI/Web adapter readiness.

## Out of Scope

- Cloud accounts.
- Multi-user collaboration.
- Hosted deployment.
- Solver-specific file generation.

## Implementation Tasks

- [x] 1. Define platform workspace layout.
  - Include `inputs/`, `state/`, `schema/`, `solver-input/`, `logs/`, `results/`, `reports/`, and `package/`.
  - _Requirement: PRD 9, PRD 11.1_

- [x] 2. Implement task state persistence.
  - Store task id, title, language, physics domain, domain pack, stage, timestamps, errors, and artifacts.
  - _Requirement: PRD 10, PRD 14_

- [x] 3. Implement artifact registry.
  - Track original inputs, schema snapshots, solver input, logs, results, reports, and final package.
  - _Requirement: PRD 9_

- [x] 4. Implement user checkpoint model.
  - Support clarification questions, default approval, extracted-value confirmation, and stop/pause decisions.
  - _Requirement: PRD 13.2_

- [x] 5. Define workflow controller interface.
  - Support intake, schema drafting, validation, solver selection, input generation, execution, postprocessing, and delivery.
  - _Requirement: PRD 10_

- [x] 6. Prepare local-first UI/control surface.
  - Keep domain-specific details hidden unless needed for diagnosis.
  - Preserve future CLI/Web adapter boundaries.
  - _Requirement: PRD 11.1_

## Acceptance Criteria

- When a user creates a simulation task, the system shall create a complete local workspace.
- When inputs are attached, the system shall register them without mutating originals.
- When a checkpoint is required, the workflow shall pause and record the user decision.
- When artifacts are generated, they shall be discoverable through stable references.
- When a future adapter is added, it shall be able to reuse the same workflow controller.

## Implementation Evidence

- Implemented workspace/task/artifact/checkpoint primitives in `physics-simulation-agent/physics_sim_agent/workspace.py`.
- Exported platform shell APIs from `physics-simulation-agent/physics_sim_agent/__init__.py`.
- Added workspace tests in `physics-simulation-agent/tests/test_workspace.py`.
- The GitHub CLI extension now delegates `init`, `new`, `add-file`, `add-table`, and `status` to `PlatformWorkspace`, so task state and artifact registry are shared with the core platform.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 46 tests passed.

## Test Plan

- Unit test workspace creation.
- Unit test state transitions.
- Unit test artifact registry.
- Unit test checkpoint persistence.
- Integration test mocked task flow from creation to delivery-ready.

## Done Definition

The platform can host a local simulation task independent of the chosen physics domain or solver.
