# gh-physics-sim

`gh-physics-sim` is the GitHub CLI extension for Physics Simulation Agent.

It exposes a local-first simulation workflow as:

```bash
gh physics-sim doctor
gh physics-sim init
gh physics-sim new "simulate airflow through a 2D pipe"
gh physics-sim status
```

The current version is local-first. It uses the platform Python modules for
workspace/task state, artifact registration, schema drafting, validation,
OpenFOAM case generation, mock/auto execution, reporting, and package assembly.
It does not require GitHub authentication.

## Local Install

From this directory:

```bash
chmod +x gh-physics-sim
gh extension install .
gh physics-sim --help
gh physics-sim doctor
```

If you installed an earlier local version:

```bash
gh extension remove physics-sim
gh extension install .
```

## Local Workflow

```bash
gh physics-sim init
gh physics-sim new "simulate airflow through a 2D straight pipe pressure drop" --case-name pipe-demo
gh physics-sim add-table ./params.csv
gh physics-sim draft
gh physics-sim validate
gh physics-sim generate
gh physics-sim run --mode mock
gh physics-sim report
gh physics-sim package
gh physics-sim status
```

Artifacts are written under `.physics-sim/` by default.

Example `params.csv`:

```csv
parameter,value,unit
length,2,m
diameter,0.1,m
inlet_velocity,5,m/s
outlet_pressure,0,Pa
density,1.225,kg/m^3
dynamic_viscosity,1.8e-5,Pa*s
```

## Notes

- The extension directory/repository must be named `gh-physics-sim`.
- The root executable must also be named `gh-physics-sim`.
- GitHub authentication is not required for the local MVP workflow.
- If numeric geometry, material, or boundary data is missing, `validate` or
  `generate` blocks and prints clarification questions instead of guessing.
- Use `gh physics-sim run --mode auto` to attempt local OpenFOAM or Docker
  execution. Use `--mode mock` for deterministic workflow testing.
- If the extension is separated from this workspace, set `PHYSICS_SIM_AGENT_ROOT`
  to the `physics-simulation-agent/` core directory.
