# Plan 02: Input Understanding And Geometry Reconstruction

## Goal

Transform user-provided natural language, screenshots, and tabular data into a structured draft of the CFD problem, including geometry information when enough explicit data is available.

## Product Scope

This plan covers input interpretation, parameter extraction, unit normalization, evidence tracking, and geometry reconstruction decisions. It does not generate OpenFOAM files directly.

## In Scope

- Natural-language CFD problem parsing.
- Screenshot text and parameter extraction.
- CSV/XLSX/table text parsing.
- Unit recognition and normalization.
- Geometry reconstruction from explicit dimensions and topology.
- Clarification questions when geometry or parameters are ambiguous.
- Evidence trail from extracted values back to user input.

## Out of Scope

- High-fidelity CAD reconstruction from arbitrary images.
- Automatic repair of complex CAD models.
- Expert-level CFD validation.
- Mesh generation.

## Key Decisions

- If geometry data is clear, the system should produce a simplified geometry definition.
- If geometry data is missing, inconsistent, or visually ambiguous, the system must ask the user for clarification.
- Screenshot extraction must be confirmed before extracted values are used.
- The first version should support simple 2D geometries needed by the four standard cases.

## Supported MVP Case Families

- 2D straight pipe.
- 2D bent pipe.
- Room ventilation.
- Flow around an object.

## Functional Requirements

- Parse natural-language intent, geometry, fluid, boundary conditions, and target outputs.
- Extract table parameters from CSV, XLSX, and pasted text.
- Extract visible text and numeric values from screenshots.
- Detect units and convert to canonical SI units.
- Identify missing required fields.
- Identify values that can be defaulted with user approval.
- Produce a draft geometry schema when explicit data is sufficient.
- Produce targeted clarification questions when explicit data is insufficient.

## Suggested Components

- `NaturalLanguageParser`: extracts CFD intent and coarse simulation setup.
- `ScreenshotExtractor`: extracts text, labels, dimensions, and confidence values.
- `TableParser`: extracts structured rows and columns from CSV/XLSX/text.
- `UnitNormalizer`: maps user units to SI units and detects missing units.
- `EvidenceMapper`: links each extracted value to its source.
- `GeometryDraftBuilder`: builds simple geometry definitions.
- `ClarificationPlanner`: creates minimal user questions for missing/ambiguous information.

## Geometry Reconstruction Rules

- Straight pipe requires length, diameter or height, inlet, outlet, and wall definitions.
- Bent pipe requires inlet segment, bend radius or elbow geometry, outlet segment, and wall definitions.
- Room ventilation requires room dimensions, inlet opening, outlet opening, and wall boundaries.
- Flow around object requires domain size, object type or dimensions, inlet, outlet, walls/symmetry, and object boundary.
- If a required dimension is missing, ask for it.
- If an image suggests geometry but lacks numeric dimensions, ask for dimensions rather than guessing.

## Implementation Tasks

- [ ] 1. Define input artifact metadata.
  - Track source type, file path, extraction status, language, and confidence.
  - _Requirement: PRD 7, PRD 11.1_

- [ ] 2. Implement natural-language extraction.
  - Extract simulation objective, physical domain, fluid, boundary conditions, operating conditions, and requested outputs.
  - _Requirement: PRD 9.1, PRD 12.1_

- [ ] 3. Implement table extraction.
  - Support CSV, XLSX, and pasted table text.
  - Normalize parameter names and detect units.
  - _Requirement: PRD 7.3, PRD 12.1_

- [ ] 4. Implement screenshot extraction.
  - Extract visible text, labels, dimensions, and confidence scores.
  - Require confirmation before using extracted values.
  - _Requirement: PRD 7.2, PRD 12.1_

- [ ] 5. Implement unit normalization.
  - Convert common units to SI.
  - Flag missing, conflicting, or impossible units.
  - _Requirement: PRD 13.2_

- [ ] 6. Implement simple geometry draft generation.
  - Support straight pipe, bent pipe, room ventilation, and flow around object.
  - Emit structured geometry only when data is explicit enough.
  - _Requirement: PRD 9.1, PRD 9.2_

- [ ] 7. Implement clarification generation.
  - Ask concise questions for missing geometry, physical properties, boundary conditions, and target metrics.
  - Separate mandatory questions from optional/defaultable assumptions.
  - _Requirement: PRD 11.2, PRD 12.2_

## Acceptance Criteria

- When the user submits natural language, the system shall produce a structured draft with extracted objective, geometry type, fluid, boundary conditions, and target outputs.
- When the user provides a table with dimensions or operating values, the system shall parse the values and normalize units.
- When a screenshot contains readable values, the system shall extract them and require confirmation before use.
- When geometry dimensions are sufficient for a supported case family, the system shall produce a geometry draft.
- When geometry information is ambiguous, the system shall ask targeted clarification questions instead of generating a guessed geometry.

## Test Plan

- Unit test natural-language extraction for all four MVP case families.
- Unit test CSV/XLSX parsing with common unit variants.
- Unit test screenshot extraction using mocked OCR output.
- Unit test geometry completeness checks.
- Integration test mixed natural-language plus table input.

## Dependencies

- Plan 01 for task workspace and input registration.
- Plan 03 for final CFD problem schema validation.

## Done Definition

- The system can turn user inputs into a traceable, reviewable CFD problem draft and can clearly identify what must be confirmed before OpenFOAM case generation.
