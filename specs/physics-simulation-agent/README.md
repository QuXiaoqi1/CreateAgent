# Physics Simulation Agent Spec

这是当前项目的新主线规格目录。

它由 `specs/cfd-openfoam-agent/` 升级而来，产品战略从“单一 CFD/OpenFOAM Agent”升级为“通用物理模拟 Agent 平台”，但 MVP 仍然只实现 CFD/OpenFOAM domain pack。

## Relationship To CFD Spec

- `specs/cfd-openfoam-agent/`：第一版领域需求来源，聚焦 CFD/OpenFOAM。
- `specs/physics-simulation-agent/`：平台版主线规格，包含通用物理模拟底座和 CFD/OpenFOAM MVP 域包。

## Current Artifacts

- `PRD.md`：平台版产品需求。
- `plans/`：8 个模块计划。
- `goals/`：8 个可复制的 `/goal` 指令。

## Recommended Next Step

从以下目标开始执行：

`goals/02-physics-problem-schema.goal.md`

原因：Physics Problem Schema 是领域识别、solver registry、OpenFOAM case 生成、执行和报告共同依赖的契约。

如果当前优先级变成先做 GitHub CLI 产品入口，可以先执行：

`goals/09-github-cli-extension.goal.md`

建议先做 `doctor/init/new/status` 的 mock 闭环，再逐步接入 schema、registry、OpenFOAM case 生成和执行引擎。
