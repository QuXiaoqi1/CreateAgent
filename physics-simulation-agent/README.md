# Physics Simulation Agent

This directory contains the implementation modules for the Physics Simulation
Agent platform.

The current milestone implements the local MVP core for a Physics Simulation
Agent: intake, schema validation, OpenFOAM case generation, staged execution,
reporting, delivery packaging, and release-readiness checks.

## Run Tests

```bash
python3 -m unittest discover physics-simulation-agent/tests
```

## Generate Release Readiness

```bash
python3 -c 'import sys; from pathlib import Path; sys.path.insert(0, "physics-simulation-agent"); from physics_sim_agent import run_release_readiness; run_release_readiness(Path("physics-simulation-agent"), Path("physics-simulation-agent/release-readiness"))'
```

## Current Scope

- Generic `problem.schema.json` model.
- Local workspace, task state, artifact registry, checkpoint, and workflow-stage primitives.
- Input artifacts for natural language, screenshot text, CSV, XLSX, and pasted tables.
- Domain classification for CFD, heat transfer, solid mechanics, PDE, multibody, multiphysics, and unknown requests.
- Unit normalization for common engineering units.
- Schema draft generation and clarification question planning.
- Provenance and assumption tracking.
- Validation result contract.
- CFD/OpenFOAM domain extension hook.
- Solver registry and adapter interface.
- OpenFOAMAdapter registration shell.
- Template-driven OpenFOAM case structure generation for four CFD MVP golden cases.
- OpenFOAM `run.sh` and `generation-manifest.json` output.
- Execution environment detection, command logging, staged mock/local execution, and OpenFOAM log parsing.
- Docker/OpenFOAM fallback command orchestration.
- Validation evidence, bilingual report generation, and reproducible delivery packages.
- Release-readiness report generation with pass/fail/skip/risk status.
- Planned future domain-pack metadata without false execution support.
- MVP validation for supported CFD case families.
- Draft-only handling for non-MVP physics domains.
