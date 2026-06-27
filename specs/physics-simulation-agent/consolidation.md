# Physics Simulation Agent Consolidation

生成日期：2026-06-27

## Overall Status

本文件已重新从 `specs/physics-simulation-agent/plans/*/plan.md` 的 9 个计划整合生成，并补入本轮 active goal/目标模式开发证据。

Physics Simulation Agent MVP 主线已经形成一个本地可运行闭环：

- 平台底座：workspace、task state、artifact registry、checkpoint、workflow stages。
- 通用 schema：Physics Problem Schema、provenance、assumption、validation。
- 输入理解：自然语言、CSV/XLSX/粘贴表格、截图提取结果占位。
- Solver 架构：domain pack metadata、registry、adapter interface、OpenFOAMAdapter。
- CFD/OpenFOAM MVP：二维直管、二维弯管、房间通风、绕流四类黄金案例。
- 执行引擎：本机 OpenFOAM 检测、Docker/OpenFOAM fallback 命令、mock execution、日志解析、失败诊断。
- 交付：validation evidence、双语 report、delivery package。
- Readiness：黄金案例、非 MVP draft-only、mock 全流程、条件式真实 smoke test。
- GitHub CLI extension：`gh physics-sim` 本地入口，已接入核心 workspace/task/artifact API 和后续模拟 workflow。

当前 release readiness 为 `ready_with_limitations`。原因是本机没有检测到 OpenFOAM 或 Docker，所以真实 smoke test 已优雅跳过；mock 全流程和核心测试已通过。

## Goal Mode Execution

本轮已经补上“进入 Codex 目标模式并发送提示词”的实际闭环。

当前 active goal 提示词：

```text
我需要补上这个步骤，现在调整为目标模式，发送提示词，开发一轮后把所有的plan.md整合为一个consolidation.md
```

本轮开发目标来自上一版 consolidation 的下一轮优先级 1：

- 统一 `gh-physics-sim init/new/add-* /status` 与 `PlatformWorkspace`。
- 让 CLI 的工作区、任务状态和 artifact registry 走核心平台 API。
- 开发完成后重新从所有 plan.md 整合本文件。

详细记录见：

- `specs/physics-simulation-agent/goal-mode-execution.md`
- `specs/physics-simulation-agent/goals/README.md`

## Plan Status

| Plan | Status | Evidence |
| --- | --- | --- |
| 01 Platform Product Shell | Done | `physics_sim_agent/workspace.py`; `tests/test_workspace.py`; CLI `init/new/add-file/add-table/status` now delegate to `PlatformWorkspace` |
| 02 Physics Problem Schema | Done | `schema.py`, `validation.py`, schema fixtures, `tests/test_schema.py` |
| 03 Domain Intake And Clarification | Done | `intake.py`, domain examples, `tests/test_intake.py` |
| 04 Solver Registry And Adapter Interfaces | Done | `adapters.py`, `registry.py`, `tests/test_registry.py` |
| 05 CFD OpenFOAM Domain Pack | Done | `openfoam_case.py`, four CFD golden cases, `tests/test_openfoam_case.py` |
| 06 Execution Environment And Engine | Done | `execution.py`, local/Docker/mock staged execution, `tests/test_execution.py` |
| 07 Validation, Report, And Delivery | Done | `delivery.py`, report/package tests, delivery package builder |
| 08 Testing And Production Readiness | Done | `readiness.py`, `release-readiness/`, `tests/test_readiness.py` |
| 09 GitHub CLI Extension | Done | `gh-physics-sim/`, Python platform bridge, CLI workflow test validates artifact registry and status output |

## Current Development Round

本轮目标模式开发完成以下改动：

- `gh-physics-sim/lib/physics_sim_cli.py`
  - 新增 `init`、`new`、`add-file`、`add-table`、`status`。
  - 这些命令现在调用 `PlatformWorkspace` 创建 workspace、任务、输入 artifact 和状态输出。
- `gh-physics-sim/gh-physics-sim`
  - 将 `init/new/add-file/add-table/status` 转发给 Python platform bridge。
- `physics-simulation-agent/physics_sim_agent/workspace.py`
  - 扩展 workflow 状态：`blocked`、`draft_only`、`human_review`、`skipped`、`failed`。
- `gh-physics-sim/tests/test_cli_workflow.py`
  - 增加对 artifact registry、`workspace.json` 和 `status` 输出的验证。
- `specs/physics-simulation-agent/plans/01-platform-product-shell/plan.md`
  - 更新 CLI 使用核心 workspace API 的 evidence。
- `specs/physics-simulation-agent/plans/09-github-cli-extension/plan.md`
  - 更新 CLI 全流程命令接入核心模块的 evidence。

## Verification

- Core tests: `python3 -m unittest discover physics-simulation-agent/tests`
- Latest result: 46 tests passed.
- CLI tests: `python3 -m unittest discover gh-physics-sim/tests`
- Latest result: 1 integration test passed.
- Goal-mode execution record:
  - `specs/physics-simulation-agent/goal-mode-execution.md`
- Readiness artifact:
  - `physics-simulation-agent/release-readiness/release-readiness.md`
  - `physics-simulation-agent/release-readiness/release-readiness.json`

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
gh physics-sim status
```

Use `gh physics-sim run --mode auto` only when local OpenFOAM or Docker/OpenFOAM is available.

## Known Limitations

- Real OpenFOAM/Docker smoke test was not executed on this machine because neither runtime is installed.
- Docker fallback command path exists, but the default image and host mount behavior still need a real Docker validation pass.
- Screenshot support currently assumes extracted text is already available; no OCR or image understanding pipeline is implemented.
- Reports are Markdown only; PDF export, plots, ParaView automation, and richer numerical postprocessing are not implemented.
- Non-CFD domains remain draft-only and deliberately cannot generate solver input.
- Geometry reconstruction is template-based for MVP cases, not a CAD repair or meshing system.
- Engineering credibility is limited to workflow evidence; results still require expert review before operational use.

## Gaps Versus PRD

- Real local OpenFOAM or Docker/OpenFOAM execution still needs a passing smoke test.
- Screenshot/OCR ingestion is not implemented; only screenshot-derived text artifacts are modeled.
- Report output lacks PDF export and rich visualization artifacts.
- Future domain packs such as heat-transfer, solid-mechanics, PDE, multibody, and multiphysics are intentionally draft-only.

## Next Iteration Priorities

1. Run and fix a real Docker/OpenFOAM straight-pipe smoke test with a pinned image.
2. Add interactive clarification flow to the CLI for missing dimensions, units, assumptions, and screenshot-derived values.
3. Add screenshot/OCR ingestion and explicit user confirmation for extracted values.
4. Expand result postprocessing with pressure drop, ventilation low-speed summaries, wake indicators, plots, and optional PDF export.
5. Add the next domain pack only after CFD MVP real-runtime validation is stable; heat-transfer is the best next candidate.

## Completion Judgment

本轮目标模式步骤已补齐：已经在 active goal 下发送目标提示词，完成一轮实际开发，并从 9 个 `plan.md` 重新整合出本 consolidation。

当前 MVP 适合本地 workflow 开发、CLI demo、完整表格输入、mock execution、交付包生成和后续 real-solver hardening。它还不能宣称生产级数值可靠，直到至少一个真实 OpenFOAM 或 Docker smoke test 在可控环境中通过。
