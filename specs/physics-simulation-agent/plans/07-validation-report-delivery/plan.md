# Plan 07: Validation, Report, And Delivery

## Goal

Generate reproducible delivery packages and user-readable reports that distinguish runnable status, numerical convergence, sanity checks, assumptions, limitations, and confidence.

## Scope

This plan covers postprocessing summaries, validation evidence, reporting, language behavior, and final package assembly.

## In Scope

- Run status summary.
- Mesh/log/convergence summary.
- Basic physics sanity checks.
- Case-family metrics for CFD MVP.
- Bilingual report behavior.
- Delivery package assembly.

## Out of Scope

- Formal certification.
- Enterprise report templates.
- Full ParaView automation.
- Expert sign-off.

## Implementation Tasks

- [x] 1. Define validation evidence model.
  - Store runnable status, convergence status, mesh status, sanity checks, warnings, and confidence.
  - _Requirement: PRD 13.5_

- [x] 2. Implement OpenFOAM MVP metrics.
  - Extract pipe pressure drop, bend loss indicators, ventilation low-speed zones, and wake/drag proxy where available.
  - _Requirement: PRD 11.7_

- [x] 3. Implement sanity check framework.
  - Include unit consistency, boundary completeness, mass/flow balance where applicable, and convergence status.
  - _Requirement: PRD 14_

- [x] 4. Implement language selection.
  - Follow user input language; default first version to Chinese plus English.
  - _Requirement: PRD 3_

- [x] 5. Implement report generator.
  - Include objective, inputs, assumptions, solver setup, environment, mesh, convergence, results, limitations, confidence, and reproduction.
  - _Requirement: PRD 9, PRD 13.5_

- [x] 6. Implement delivery package builder.
  - Assemble schema, assumptions, solver input, logs, results, report, metadata, and optional archive.
  - _Requirement: PRD 9_

## Acceptance Criteria

- When a simulation completes, the report shall include runnable status and convergence status.
- When a simulation fails, the package shall include stage, raw logs, diagnosis, and next steps.
- When a report is generated, it shall avoid overclaiming and include limitations.
- When a package is exported, it shall contain enough files to reproduce the run.

## Implementation Evidence

- Implemented validation evidence, metrics, report generation, and package assembly in `physics-simulation-agent/physics_sim_agent/delivery.py`.
- Exported delivery APIs from `physics-simulation-agent/physics_sim_agent/__init__.py`.
- Added package/report coverage in `physics-simulation-agent/tests/test_delivery.py`.
- Verification command: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 36 tests passed.

## Test Plan

- Unit test validation evidence summaries.
- Unit test report generation from fixture artifacts.
- Unit test language selection.
- Unit test package content completeness.
- Snapshot test report markdown.

## Done Definition

The user receives a complete package that explains what was run, how trustworthy it is, and how to reproduce it.
