# Physics Simulation Agent Consolidation

生成日期：2026-06-27

## Overall Status

Physics Simulation Agent MVP 主线已经形成一个本地可运行闭环：

- 平台底座：workspace、task state、artifact registry、checkpoint、workflow stages。
- 通用 schema：Physics Problem Schema、provenance、assumption、validation。
- 输入理解：自然语言、CSV/XLSX/粘贴表格、截图提取结果占位。
- Solver 架构：domain pack metadata、registry、adapter interface、OpenFOAMAdapter。
- CFD/OpenFOAM MVP：二维直管、二维弯管、房间通风、绕流四类黄金案例。
- 执行引擎：本机 OpenFOAM 检测、Docker/OpenFOAM fallback 命令、mock execution、日志解析、失败诊断。
- 交付：validation evidence、双语 report、delivery package。
- Readiness：黄金案例、非 MVP draft-only、mock 全流程、条件式真实 smoke test。
- GitHub CLI extension：`gh physics-sim` 本地入口，接入核心模块。

当前 release readiness 为 `ready_with_limitations`。原因是本机没有检测到 OpenFOAM 或 Docker，所以真实 smoke test 已优雅跳过；mock 全流程和核心测试已通过。

## Goal Mode Execution

本轮补齐了“进入 Codex 目标模式并发送 `/goal` 提示词”的流程证据。之前已经生成了 9 个 goal 文件，也实际执行了多个目标，但没有把“目标模式执行”作为独立门槛记录在 consolidation 中。

当前记录见：

- `specs/physics-simulation-agent/goal-mode-execution.md`
- `specs/physics-simulation-agent/goals/README.md`

## Plan Status

| Plan | Status | Evidence |
| --- | --- | --- |
| 01 Platform Product Shell | Done | `physics_sim_agent/workspace.py`, `tests/test_workspace.py` |
| 02 Physics Problem Schema | Done | `schema.py`, `validation.py`, schema fixtures |
| 03 Domain Intake And Clarification | Done | `intake.py`, domain examples, clarification tests |
| 04 Solver Registry And Adapter Interfaces | Done | `adapters.py`, `registry.py` |
| 05 CFD OpenFOAM Domain Pack | Done | `openfoam_case.py`, four CFD golden cases |
| 06 Execution Environment And Engine | Done | `execution.py`, local/Docker/mock staged execution |
| 07 Validation, Report, And Delivery | Done | `delivery.py`, report/package tests |
| 08 Testing And Production Readiness | Done | `readiness.py`, `release-readiness/` artifacts |
| 09 GitHub CLI Extension | Done | `gh-physics-sim/`, platform bridge, CLI workflow test |

## Verification

- Core tests: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 46 tests passed.
- CLI tests: `python3 -m unittest discover gh-physics-sim/tests`
- Latest result: 1 integration test passed.
- Installed extension checks:
  - `gh physics-sim --help` passed.
  - `gh physics-sim doctor` passed.
- Readiness artifact:
  - `physics-simulation-agent/release-readiness/release-readiness.md`
  - `physics-simulation-agent/release-readiness/release-readiness.json`
- Goal-mode execution record:
  - `specs/physics-simulation-agent/goal-mode-execution.md`

## Current Product Path

Recommended local workflow:

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
```

Use `gh physics-sim run --mode auto` only when local OpenFOAM or Docker/OpenFOAM is available.

## Known Limitations

- Real OpenFOAM/Docker smoke test was not executed on this machine because neither runtime is installed.
- Docker fallback command path exists, but the default image and host mount behavior still need a real Docker validation pass.
- Screenshot support currently assumes extracted text is already available; no OCR or image understanding pipeline is implemented.
- CLI `init/new/add-*` and the new `PlatformWorkspace` module share the same layout but are not fully unified behind one Python API yet.
- Reports are Markdown only; PDF export, plots, ParaView automation, and richer numerical postprocessing are not implemented.
- Non-CFD domains remain draft-only and deliberately cannot generate solver input.
- Geometry reconstruction is template-based for MVP cases, not a CAD repair or meshing system.
- Engineering credibility is limited to workflow evidence; results still require expert review before operational use.

## Next Iteration Priorities

1. Unify `gh-physics-sim init/new/add-*` with `PlatformWorkspace` so all task state and artifacts use one core API.
2. Run and fix a real Docker/OpenFOAM straight-pipe smoke test with a pinned image.
3. Add interactive clarification flow to the CLI for missing dimensions, units, assumptions, and screenshot-derived values.
4. Add screenshot/OCR ingestion and explicit user confirmation for extracted values.
5. Expand result postprocessing with pressure drop, ventilation low-speed summaries, wake indicators, plots, and optional PDF export.
6. Add the next domain pack only after CFD MVP real-runtime validation is stable; heat-transfer is the best next candidate.

## Completion Judgment

The MVP is now suitable for local workflow development, CLI demos with complete tabular inputs, mock execution, package generation, and further real-solver hardening. It is not yet suitable to claim production numerical reliability until at least one real OpenFOAM or Docker smoke test passes on a controlled environment.
