# Plan 03: Domain Intake And Clarification

## Goal

Turn natural language, screenshots, tables, and files into a Physics Problem Schema draft, identify the physics domain, and ask targeted clarification questions.

## Scope

This plan covers input understanding and domain classification. It does not generate solver input.

## In Scope

- Natural-language intake.
- Screenshot extraction result handling.
- CSV/XLSX/pasted-table parsing.
- Physics domain classification.
- Unit normalization.
- Geometry and parameter completeness checks.
- Clarification question generation.

## Out of Scope

- Complex CAD reconstruction.
- Paid OCR/LLM service integration.
- Solver execution.

## MVP Behavior

- CFD/OpenFOAM requests that match MVP scope continue toward solving.
- Non-MVP domains produce a structured draft and a clear unsupported-domain explanation.
- Ambiguous inputs ask the minimum necessary questions.

## Implementation Tasks

- [x] 1. Implement input artifact parser interface.
  - Normalize text, table, screenshot extraction results, and files into typed artifacts.
  - _Requirement: PRD 8_

- [x] 2. Implement physics domain classifier.
  - Classify CFD, heat-transfer, solid-mechanics, PDE, multibody, multiphysics, or unknown.
  - _Requirement: PRD 10, PRD 13.1_

- [x] 3. Implement unit and value normalization.
  - Convert common engineering units and flag missing or conflicting units.
  - _Requirement: PRD 7.1_

- [x] 4. Implement schema draft builder.
  - Populate objective, domain, geometry, materials, conditions, targets, and provenance.
  - _Requirement: PRD 11.2_

- [x] 5. Implement clarification planner.
  - Separate blocking questions, optional defaults, unsupported-domain messages, and expert-review warnings.
  - _Requirement: PRD 13.2_

- [x] 6. Add MVP CFD geometry draft rules.
  - Support straight pipe, bent pipe, room ventilation, and flow around object when data is explicit.
  - _Requirement: PRD 3, PRD 11.5_

## Implementation Evidence

- Implemented intake and clarification in `physics-simulation-agent/physics_sim_agent/intake.py`.
- Added domain example fixtures in `physics-simulation-agent/fixtures/domain_examples.json`.
- Added intake tests in `physics-simulation-agent/tests/test_intake.py`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 24 tests passed.

## Acceptance Criteria

- When a user submits a physics request, the system shall classify the likely physics domain.
- When a request is non-MVP, the system shall not claim automatic solving support.
- When required parameters are missing, the system shall ask targeted questions.
- When screenshot-derived values are used, the system shall require confirmation.
- When CFD/OpenFOAM inputs are explicit, the system shall produce a schema draft suitable for validation.

## Test Plan

- Unit test classification examples for CFD, heat, solid, PDE, multibody, multiphysics, and unknown.
- Unit test table parsing and unit normalization.
- Unit test clarification generation.
- Integration test natural language plus table to schema draft.

## Done Definition

The platform can understand what kind of physics problem the user described and either draft a solvable MVP schema or explain what is missing.
