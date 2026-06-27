# Physics Simulation Agent Goal Prompts

本目录是平台版第 3 步产物：将每个 plan.md 转成可复制的 Codex `/goal` 指令。

## 推荐执行顺序

1. `02-physics-problem-schema.goal.md`
2. `04-solver-registry-adapters.goal.md`
3. `01-platform-product-shell.goal.md`
4. `03-domain-intake-clarification.goal.md`
5. `05-cfd-openfoam-domain-pack.goal.md`
6. `06-execution-environment-engine.goal.md`
7. `07-validation-report-delivery.goal.md`
8. `08-testing-production-readiness.goal.md`
9. `09-github-cli-extension.goal.md`

## 使用方式

复制每个文件里的“推荐执行版（中文，可直接复制）”到 Codex 目标模式。

建议一次只执行一个目标。完成后记录完成项、测试证据、风险和遗漏，再进入下一个目标。这样最终生成 `consolidation.md` 时会更准确。

## 当前策略

- 产品战略：Physics Simulation Agent 平台。
- MVP 实现：CFD/OpenFOAM domain pack。
- 第一产品入口：GitHub CLI extension，建议仓库名 `gh-physics-sim`，命令名 `gh physics-sim`。
- 后续扩展：FEniCSx、MOOSE、Chrono 等 solver adapter。
