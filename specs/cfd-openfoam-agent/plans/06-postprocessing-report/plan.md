# Plan 06: Postprocessing, Analysis Report, And Delivery Package

## Goal

Convert completed OpenFOAM runs into a complete delivery package with results, logs, assumptions, metadata, and a bilingual analysis report understandable to non-CFD users.

## Product Scope

This plan covers result extraction, convergence summary, metric calculation, report generation, language behavior, and final package assembly.

## In Scope

- Residual and convergence summary.
- Mesh quality summary.
- Key metric extraction.
- Basic result tables and charts.
- Non-expert analysis report.
- Chinese and English default output.
- Input-language-based report language selection.
- Delivery package assembly.

## Out of Scope

- Full ParaView automation in MVP.
- Advanced 3D visualization.
- Formal engineering certification.
- Enterprise report templates unless later specified.

## Key Decisions

- First version defaults to Chinese plus English.
- If the user's input language is clearly one language, report language should follow the user's language while still allowing bilingual output.
- The report must explain assumptions, limitations, and confidence.
- Raw logs and generated case files must remain included for reproducibility.

## Delivery Package Structure

- `README.md`
- `assumptions.md`
- `case/`
- `run.sh`
- `logs/`
- `results/`
- `report.md`
- `metadata.json`
- Optional `report.pdf`
- Optional compressed archive

## Functional Requirements

- Parse execution logs and extract convergence status.
- Parse mesh check results.
- Extract case-family-specific key metrics.
- Generate summary tables or basic charts where possible.
- Generate `assumptions.md`.
- Generate `metadata.json`.
- Generate a non-expert analysis report.
- Assemble all files into a delivery folder.
- Support export as a compressed package.

## Case-Family Metrics

- Straight pipe: pressure drop, velocity profile summary, mass flow consistency.
- Bent pipe: pressure drop, bend loss indicators, velocity acceleration zones.
- Room ventilation: inlet/outlet flow balance, low-velocity zones, basic air movement interpretation.
- Flow around object: pressure distribution indicators, wake region summary, drag-related proxy if available.

## Report Sections

- Problem summary.
- Inputs and assumptions.
- Generated simulation setup.
- OpenFOAM environment and solver.
- Mesh quality summary.
- Convergence and execution status.
- Key results.
- Interpretation for non-CFD users.
- Reliability and limitations.
- Recommended next steps.
- Reproduction instructions.

## Implementation Tasks

- [ ] 1. Define result artifact model.
  - Track logs, sampled data, generated plots, report files, and package files.
  - _Requirement: PRD 8, PRD 11.7_

- [ ] 2. Implement convergence summary.
  - Convert solver log parser outputs into user-facing convergence status.
  - _Requirement: PRD 11.6, PRD 12.5_

- [ ] 3. Implement case-family metric extraction.
  - Extract or compute MVP metrics for all four standard cases.
  - _Requirement: PRD 9.5_

- [ ] 4. Implement basic chart/table generation.
  - Generate compact visual or tabular summaries where data is available.
  - Keep raw data files in `results/`.
  - _Requirement: PRD 9.5_

- [ ] 5. Implement report language selection.
  - Detect user input language.
  - Default to Chinese plus English in first version.
  - Allow report generation to follow user language.
  - _Requirement: PRD 15_

- [ ] 6. Implement report generator.
  - Generate `report.md` with non-expert explanations and technical appendix references.
  - Include assumptions, limitations, and recommended next steps.
  - _Requirement: PRD 12.5, PRD 13.4_

- [ ] 7. Implement delivery package assembly.
  - Collect inputs, schema snapshot, assumptions, case files, logs, results, metadata, and report.
  - Produce a stable folder and optional archive.
  - _Requirement: PRD 8, PRD 11.7_

## Acceptance Criteria

- When a solver completes, the system shall generate a convergence summary and include it in the report.
- When mesh checking has run, the report shall summarize critical mesh quality status.
- When a standard case completes, the system shall extract case-family-specific key metrics where data is available.
- When a report is generated, it shall explain results in non-expert language and include assumptions, limitations, and next steps.
- When the delivery package is exported, it shall contain all files needed to reproduce the simulation in a compatible OpenFOAM environment.

## Test Plan

- Unit test report generation with fixture task data.
- Unit test language selection.
- Unit test package assembly.
- Unit test metric extraction for each case family with fixture result data.
- Snapshot test generated `report.md`.

## Dependencies

- Plan 01 for artifact registry.
- Plan 03 for schema and assumptions.
- Plan 05 for logs and execution outputs.

## Done Definition

- A successful simulation produces a complete delivery package that a non-CFD user can read, share, and reproduce.
