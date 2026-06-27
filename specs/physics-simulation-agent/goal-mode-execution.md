# Goal Mode Execution Record

生成日期：2026-06-27

## Answer

这一步之前做过一部分，但没有作为独立证据写进仓库。

已经完成的部分：

- 已使用 `qiaomu-goal-meta-skill` 为每个 plan 生成 `/goal` 提示词。
- 已在 `specs/physics-simulation-agent/goals/README.md` 写明：把每个目标文件中的推荐执行版复制到 Codex 目标模式。
- 早期目标由用户逐条触发执行，例如 02、04、03、05。
- 后续 06-08 曾进入 active goal/目标模式连续执行，并生成 readiness 与 consolidation。

之前缺失的部分：

- 没有单独记录“第 4 步：把 Codex 调成目标模式，然后发送对应 `/goal` 提示词”的执行证据。
- consolidation 里没有把 goal-mode execution 作为流程门槛列出来。

本文件用于补齐这个流程证据。

## Required Loop Step

在生产级 agent 生成循环中，`goals/*.goal.md` 生成后必须执行以下步骤：

1. 选择一个目标文件，例如 `goals/06-execution-environment-engine.goal.md`。
2. 进入 Codex 目标模式。
3. 发送该文件中的“推荐执行版（中文，可直接复制）” `/goal` 提示词。
4. 在目标模式内执行实现、测试、验收证据写回。
5. 目标完成后记录：
   - 执行的 goal 文件。
   - 主要实现文件。
   - 验证命令和结果。
   - 未完成限制或下一轮事项。

## Current Execution Mapping

| Goal | Current Evidence |
| --- | --- |
| 01 Platform Product Shell | `physics_sim_agent/workspace.py`, `tests/test_workspace.py`, `plans/01.../plan.md` evidence |
| 02 Physics Problem Schema | `schema.py`, `validation.py`, `tests/test_schema.py` |
| 03 Domain Intake And Clarification | `intake.py`, `tests/test_intake.py` |
| 04 Solver Registry And Adapter Interfaces | `adapters.py`, `registry.py`, `tests/test_registry.py` |
| 05 CFD OpenFOAM Domain Pack | `openfoam_case.py`, `fixtures/cfd_golden_cases.json`, `tests/test_openfoam_case.py` |
| 06 Execution Environment And Engine | `execution.py`, `tests/test_execution.py` |
| 07 Validation, Report, And Delivery | `delivery.py`, `tests/test_delivery.py` |
| 08 Testing And Production Readiness | `readiness.py`, `release-readiness/`, `tests/test_readiness.py` |
| 09 GitHub CLI Extension | `gh-physics-sim/`, `tests/test_cli_workflow.py` |

## Goal Mode Run: 2026-06-27 Follow-up Loop

本轮已在 active goal/目标模式下执行。用户发送的目标提示词为：

```text
我需要补上这个步骤，现在调整为目标模式，发送提示词，开发一轮后把所有的plan.md整合为一个consolidation.md
```

本轮开发目标选择：

- 来源：`specs/physics-simulation-agent/consolidation.md` 的下一轮优先级 1。
- 目标：统一 `gh-physics-sim init/new/add-* /status` 与 `PlatformWorkspace`，让 CLI 的工作区、任务状态和 artifact registry 走核心平台 API。

本轮实现：

- `gh-physics-sim/lib/physics_sim_cli.py` 新增 `init`、`new`、`add-file`、`add-table`、`status` 命令。
- `gh-physics-sim/gh-physics-sim` 将这些命令转发给 Python platform bridge。
- `physics-simulation-agent/physics_sim_agent/workspace.py` 扩展真实 workflow 状态：`blocked`、`draft_only`、`human_review`、`skipped`、`failed`。
- `gh-physics-sim/tests/test_cli_workflow.py` 增加 artifact registry 和 status 输出验证。

本轮验证：

- `python3 -m unittest discover physics-simulation-agent/tests`
- `python3 -m unittest discover gh-physics-sim/tests`

本轮 consolidation 要求：

- 重新读取 9 个 `plans/*/plan.md`。
- 将本轮开发证据整合进 `specs/physics-simulation-agent/consolidation.md`。
- 标明当前仍未完成的是 real OpenFOAM/Docker smoke、OCR/screenshot ingestion、PDF/plot 等后续能力，而不是目标模式流程本身。

## Verification

- Core tests: `python3 -m unittest discover physics-simulation-agent/tests`
- CLI tests: `python3 -m unittest discover gh-physics-sim/tests`
- Goal prompts: `specs/physics-simulation-agent/goals/*.goal.md`
- Consolidation: `specs/physics-simulation-agent/consolidation.md`

## Future Rule

以后开发新的 agent 时，不要只生成 `/goal` 文件。必须明确进入目标模式并发送目标提示词；如果因为环境限制无法真正进入目标模式，就必须在 consolidation 中标记为未执行，而不是默认完成。
