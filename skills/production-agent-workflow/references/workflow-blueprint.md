# Production Agent Workflow Blueprint

Use these templates when creating artifacts for a new agent.

## Directory Layout

```text
specs/<agent-name>/
├── PRD.md
├── plans/
│   ├── README.md
│   ├── 01-product-shell/plan.md
│   ├── 02-core-schema/plan.md
│   └── ...
├── goals/
│   ├── README.md
│   ├── 01-product-shell.goal.md
│   ├── 02-core-schema.goal.md
│   └── ...
├── goal-mode-execution.md
└── consolidation.md
```

Implementation may live beside specs, for example:

```text
<agent-name>/
<agent-name>-cli/
<agent-name>-web/
```

## PRD Template

```markdown
# <Agent Name> PRD

版本：
状态：
阶段：

## 1. 产品定位

一句话目标：

## 2. 目标用户

## 3. 用户问题

## 4. 产品目标

## 5. MVP 边界

MVP 实现：

MVP 不实现：

## 6. 输入范围

## 7. 输出交付包

## 8. 核心流程

1. ...

## 9. 核心概念和数据契约

## 10. 架构

- Platform core:
- Domain/tool packs:
- Adapters:
- Product surfaces:

## 11. 错误、诊断和人工介入

## 12. 测试和生产就绪

## 13. 风险和开放问题
```

## Plan Template

```markdown
# Plan NN: <Title>

## Goal

## Scope

## In Scope

## Out of Scope

## Implementation Tasks

- [ ] 1. ...
  - _Requirement: PRD X_

## Acceptance Criteria

- When ..., the system shall ...

## Test Plan

## Done Definition

## Implementation Evidence

- Add this section only after implementation starts.
```

## Goal Prompt Template

```text
/goal 基于 specs/<agent-name>/PRD.md 和 specs/<agent-name>/plans/NN-<slug>/plan.md，完成 <specific outcome>。
验证：先读取 PRD、对应 plan 和当前实现；发现项目已有测试/构建/运行命令；实现后运行最小完整验证；保存或记录关键输出。
约束：不扩大 MVP 范围；不跳过验收标准；不强制安装外部依赖；不伪造真实集成成功。
边界：只写入与本 plan 直接相关的实现、测试、fixtures、文档和验收状态；不做无关重构。
迭代策略：先实现可测试合同，再接入真实模块；每次失败先读日志；同一失败连续 2 次后缩小到最小复现。
完成条件：plan 的核心任务完成，测试通过，验收证据写回 plan。
暂停条件：需要凭证、付费服务、生产数据、破坏性操作、系统安装权限、或用户决定改变产品范围。
```

## Default Plan Sequence

1. **Product Shell**
   - Workspace, task state, artifact registry, checkpoints, workflow stages.
2. **Core Schema**
   - Canonical task/problem schema, provenance, assumptions, validation.
3. **Intake And Clarification**
   - Natural language/files/tables/screenshots, classification, missing-info questions.
4. **Registry And Adapters**
   - Tool/domain registry, capability checks, adapter interface.
5. **First Domain Or Tool Pack**
   - The first real executable use case.
6. **Execution Engine**
   - Runtime detection, command/API orchestration, logs, retries, failure diagnosis.
7. **Validation And Delivery**
   - Evidence model, reports, package/export.
8. **Testing And Readiness**
   - Unit tests, integration tests, mock full workflow, conditional real smoke tests.
9. **Product Surface**
   - CLI, Web, desktop, plugin, API, or automation surface.

## Goal Mode Execution Template

```markdown
# Goal Mode Execution Record

## Answer

State whether goal mode was actually used, partially used, or not yet used.

## Required Loop Step

1. Select one `goals/*.goal.md` file.
2. Enter Codex goal mode.
3. Send the recommended `/goal` block.
4. Execute until complete, blocked, or user decision required.
5. Record implementation and verification evidence in the matching `plan.md`.

## Current Execution Mapping

| Goal | Current Evidence |
| --- | --- |

## Verification

## Future Rule

Do not count `/goal` files as executed unless they were sent in goal mode or explicitly marked as not executed.
```

## Readiness Template

```markdown
# <Agent Name> Release Readiness

Overall status: `ready|ready_with_limitations|not_ready`

## Checks

| Check | Status | Message |
| --- | --- | --- |
| fixture_structure | pass | ... |
| test_surface | pass | ... |
| mock_full_workflow | pass | ... |
| conditional_real_smoke | skip | ... |

## Limitations

## Risks

## Recommendations
```

## Consolidation Template

```markdown
# <Agent Name> Consolidation

生成日期：

## Overall Status

## Plan Status

| Plan | Status | Evidence |
| --- | --- | --- |

## Verification

## Current Product Path

## Known Limitations

## Gaps Versus PRD

## Next Iteration Priorities

## Completion Judgment
```

## Quality Bar

An agent development loop is not complete until:

- A user can describe the task in product language.
- The PRD captures MVP and non-goals.
- Plans are small enough to execute independently.
- Goals include verification and pause conditions.
- At least one end-to-end workflow works in mock or local mode.
- Missing external dependencies are diagnosed, skipped, or blocked clearly.
- Consolidation names the remaining limitations without exaggeration.
