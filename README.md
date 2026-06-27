# Production Agent Generator

This repository contains a production-agent development workflow and its first
worked example: Physics Simulation Agent.

## What Is Included

- `specs/physics-simulation-agent/`: PRD, plans, goal prompts, and consolidation.
- `physics-simulation-agent/`: Python core modules for schema, intake, adapters,
  OpenFOAM case generation, execution, delivery, readiness, and workspace state.
- `gh-physics-sim/`: GitHub CLI extension exposing the local workflow as
  `gh physics-sim`.
- `skills/production-agent-workflow/`: reusable Codex skill that distills the
  PRD -> plans -> goals -> goal-mode execution -> consolidation agent
  development workflow.
- `specs/cfd-openfoam-agent/`: earlier CFD/OpenFOAM-focused planning artifacts.

## Verify

```bash
python3 -m unittest discover physics-simulation-agent/tests
python3 -m unittest discover gh-physics-sim/tests
```

## GitHub CLI Extension

From `gh-physics-sim/`:

```bash
gh extension install .
gh physics-sim --help
gh physics-sim doctor
```

## Current Readiness

The current MVP status is `ready_with_limitations`: core and CLI tests pass, the
mock workflow produces a delivery package, and real OpenFOAM/Docker execution is
skipped when those runtimes are not available.

See `specs/physics-simulation-agent/consolidation.md` for the full status and
next iteration priorities.
