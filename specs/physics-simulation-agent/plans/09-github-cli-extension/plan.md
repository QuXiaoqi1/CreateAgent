# Plan 09: GitHub CLI Extension

## Goal

Package Physics Simulation Agent as a GitHub CLI extension named `gh-physics-sim`, exposing the local-first product workflow through `gh physics-sim`.

## Scope

This plan covers the first CLI product surface. It should call the platform workflow and domain-pack modules rather than duplicating simulation logic.

## In Scope

- GitHub CLI extension repository structure.
- `gh physics-sim` command group.
- Local workspace initialization.
- Task creation and input registration.
- Schema draft and validation commands.
- Solver input generation command.
- Execution command and status command.
- Report and package commands.
- Environment diagnostic command.
- Local installation and verification flow.

## Out of Scope

- Hosted SaaS.
- Mandatory GitHub authentication.
- Required GitHub repository integration.
- Publishing releases to GitHub Marketplace.
- Remote HPC execution.
- Full Web or desktop UI.

## Key Decisions

- Extension name: `gh-physics-sim`.
- User command: `gh physics-sim`.
- First implementation should be local-first and work without GitHub login.
- Implementation language: Bash entrypoint plus Python platform bridge, because the existing GitHub CLI extension shell is Bash and the platform core modules are Python.
- The extension should call platform services through stable internal APIs.
- GitHub repository features should remain optional enhancements.

## MVP Command Design

```bash
gh physics-sim --help
gh physics-sim doctor
gh physics-sim init [--workspace .physics-sim]
gh physics-sim new "simulate airflow through a 2D pipe" [--case-name pipe-demo]
gh physics-sim add-file ./diagram.png
gh physics-sim add-table ./params.xlsx
gh physics-sim draft
gh physics-sim validate
gh physics-sim generate
gh physics-sim run
gh physics-sim status
gh physics-sim report
gh physics-sim package
```

## Workspace Behavior

- Default task directory: `.physics-sim/`.
- If inside a Git repository, do not modify tracked files unless the user explicitly selects that path.
- If outside a Git repository, use the current directory or a user-provided workspace.
- Store all task artifacts in the platform workspace layout.
- Support multiple tasks through task ids or names.

## Implementation Tasks

- [x] 1. Scaffold GitHub CLI extension structure.
  - Create `gh-physics-sim` executable entrypoint.
  - Include README, installation instructions, help text, and development commands.
  - _Requirement: PRD 3.1, PRD 11.1.1_

- [x] 2. Implement command router.
  - Provide `--help`, version, error formatting, and shared config loading.
  - _Requirement: PRD 13.6_

- [x] 3. Implement `doctor`.
  - Report GitHub CLI version, current directory, Git repository status, workspace writability, OpenFOAM availability, Docker availability, and platform config.
  - _Requirement: PRD 13.6_

- [x] 4. Implement `init`.
  - Create or locate `.physics-sim/` workspace.
  - Avoid modifying tracked files unless explicitly requested.
  - _Requirement: PRD 11.1, PRD 13.6_

- [x] 5. Implement task and input commands.
  - Support `new`, `add-file`, and `add-table`.
  - Register artifacts through the platform artifact registry.
  - _Requirement: PRD 8, PRD 11.2_

- [x] 6. Implement schema commands.
  - Support `draft` and `validate`.
  - Print concise user-facing summaries and save schema artifacts.
  - _Requirement: PRD 7.1, PRD 13.2_

- [x] 7. Implement generation and execution commands.
  - Support `generate`, `run`, and `status`.
  - Delegate solver input generation and execution to platform modules.
  - _Requirement: PRD 11.5, PRD 11.6_

- [x] 8. Implement report and package commands.
  - Support `report` and `package`.
  - Print final artifact paths and package summary.
  - _Requirement: PRD 9, PRD 13.5_

- [x] 9. Add local installation verification.
  - Support `gh extension install .` from the extension directory.
  - Verify `gh physics-sim --help` and `gh physics-sim doctor`.
  - _Requirement: PRD 13.6_

- [x] 10. Add tests.
  - Test command parsing, workspace safety, mocked workflow, doctor output, and no-login behavior.
  - _Requirement: PRD 14_

## Acceptance Criteria

- When the user installs the extension locally, `gh physics-sim --help` shall run successfully.
- When the user runs `gh physics-sim doctor`, the command shall report environment status without requiring GitHub authentication.
- When the user runs the mocked MVP command sequence, the extension shall create a task workspace and produce expected artifacts.
- When inside a Git repository, the extension shall not modify tracked files unless explicitly configured.
- When platform modules are unavailable or incomplete, the extension shall show a clear staged error instead of crashing.

## Implementation Evidence

- Implemented GitHub CLI entrypoint in `gh-physics-sim/gh-physics-sim`.
- Added platform bridge in `gh-physics-sim/lib/physics_sim_cli.py`.
- `init`, `new`, `add-file`, `add-table`, `status`, `draft`, `validate`, `generate`, `run`, `report`, and `package` now call Physics Simulation Agent core modules instead of writing mock placeholders.
- CLI workflow tests verify artifact registration under `PlatformWorkspace` and status output from the shared task state.
- Added CLI integration test in `gh-physics-sim/tests/test_cli_workflow.py`.
- Verification commands:
  - `python3 -m unittest discover gh-physics-sim/tests`
  - `gh physics-sim --help`
  - `gh physics-sim doctor`
- Latest result: CLI test passed; installed extension help and doctor passed.

## Test Plan

- Unit test command parsing.
- Unit test workspace path selection.
- Unit test Git repository safety behavior.
- Unit test doctor output with mocked environment probes.
- Integration test local mocked workflow.
- Manual verification with `gh extension install .`, `gh physics-sim --help`, and `gh physics-sim doctor`.

## Done Definition

The product can be installed as a local GitHub CLI extension and can drive the Physics Simulation Agent MVP workflow from the terminal.
