# Plan 01: Local Product Shell

## Goal

Build the first local product experience for the CFD OpenFOAM Agent. The shell should let a non-CFD user create a simulation task, provide inputs, review clarification questions, monitor execution status, and access the final delivery package.

## Product Scope

MVP prioritizes a local product experience. CLI and Web should remain possible later, but the first implementation should avoid locking the workflow into one UI surface.

## In Scope

- Local task workspace structure.
- Task creation and persistence.
- Input file registration.
- Multi-stage task status model.
- Human confirmation checkpoints.
- Delivery package browser or export entry.
- Internal API/service boundaries that can later back CLI or Web.

## Out of Scope

- Full cloud multi-user collaboration.
- Authentication and team permissions.
- Polished desktop packaging.
- Public hosted SaaS deployment.

## Key Decisions

- The product should be local-first.
- The workflow engine should be UI-agnostic.
- The first UI may be a lightweight local interface, but core logic must live outside presentation components.
- CLI should be considered a later adapter, not the primary MVP surface.

## Functional Requirements

- Users can create a new CFD task with a title and natural-language problem statement.
- Users can attach screenshots, CSV/XLSX files, and supporting documents.
- Users can see the current stage of a task.
- Users can answer clarification questions before execution continues.
- Users can review the structured simulation problem before case generation.
- Users can open or export the final delivery package.
- The product records all task inputs, decisions, logs, generated files, and report outputs.

## Suggested Architecture

- `TaskWorkspace`: creates and manages per-task folders.
- `TaskState`: stores task status, stage, timestamps, errors, and artifacts.
- `WorkflowController`: coordinates problem parsing, clarification, case generation, execution, post-processing, and delivery.
- `ArtifactRegistry`: tracks uploaded inputs and generated outputs.
- `UserCheckpoint`: records questions, default values, user answers, and approvals.
- `LocalUIAdapter`: first local product surface.
- `FutureCLIAdapter`: reserved interface for later CLI support.
- `FutureWebAdapter`: reserved interface for later Web support.

## Task Stages

- `created`
- `inputs_registered`
- `problem_drafted`
- `awaiting_user_confirmation`
- `problem_confirmed`
- `case_generated`
- `environment_checked`
- `mesh_checked`
- `solver_running`
- `postprocessing`
- `report_generated`
- `delivery_ready`
- `failed`

## Implementation Tasks

- [ ] 1. Define local task workspace layout.
  - Create a deterministic directory structure for each simulation task.
  - Include folders for inputs, intermediate state, generated case, logs, results, report, and package.
  - _Requirement: PRD 8, PRD 10, PRD 11.7_

- [ ] 2. Implement task state persistence.
  - Store task metadata, current stage, timestamps, artifact paths, user confirmations, and error state.
  - Use a structured format that can be read by future CLI/Web adapters.
  - _Requirement: PRD 13.1_

- [ ] 3. Implement input registration.
  - Register natural-language prompts, screenshots, CSV/XLSX files, and pasted table text.
  - Keep original files unchanged and attach normalized metadata.
  - _Requirement: PRD 7, PRD 11.1_

- [ ] 4. Implement checkpoint flow.
  - Support blocking clarification questions.
  - Support default-value approval.
  - Record user decisions for assumptions and auditability.
  - _Requirement: PRD 11.2, PRD 12.2_

- [ ] 5. Implement artifact registry.
  - Track generated OpenFOAM case files, logs, reports, metadata, and export packages.
  - Provide stable artifact references for UI, CLI, and Web adapters.
  - _Requirement: PRD 8, PRD 11.7_

- [ ] 6. Create first local UI or local control surface.
  - Let users create tasks, attach inputs, answer checkpoints, and open outputs.
  - Keep CFD/OpenFOAM details hidden unless needed for diagnosis.
  - _Requirement: PRD 6, PRD 13.4_

## Acceptance Criteria

- When a user creates a task, the system shall create a complete task workspace with metadata and input folders.
- When a user attaches files, the system shall register the files without mutating the originals.
- When the workflow reaches a required clarification, the system shall pause and expose the question to the user.
- When the user approves a structured problem definition, the system shall record the approval and continue to case generation.
- When the task completes, the system shall expose the delivery package through the local product shell.

## Test Plan

- Unit test task workspace creation.
- Unit test task state transitions.
- Unit test artifact registration.
- Unit test checkpoint persistence.
- Integration test a task moving from creation to delivery-ready with mocked CFD execution.

## Dependencies

- Plan 02 for parsed inputs.
- Plan 03 for structured CFD schema.
- Plan 04 for case artifacts.
- Plan 05 for execution status.
- Plan 06 for report and delivery package.

## Done Definition

- A non-CFD user can start a local task, provide inputs, answer confirmations, and retrieve an organized delivery package.
- The workflow core can later be exposed through CLI or Web without rewriting task orchestration.
