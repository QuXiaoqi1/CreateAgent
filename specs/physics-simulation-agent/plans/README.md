# Physics Simulation Agent Plans

本目录是平台版 PRD 的第 2 步拆分产物。它把原来的 CFD/OpenFOAM Agent 升级为“通用物理模拟平台 + CFD/OpenFOAM MVP 领域包”。

## Plan List

1. `01-platform-product-shell/plan.md`
   - 本地任务壳、状态、artifact、checkpoint、workflow controller。

2. `02-physics-problem-schema/plan.md`
   - 通用 Physics Problem Schema、provenance、assumption、validation。

3. `03-domain-intake-clarification/plan.md`
   - 输入理解、物理领域识别、单位归一、澄清问题。

4. `04-solver-registry-adapters/plan.md`
   - solver registry、domain pack、adapter interface、能力边界。

5. `05-cfd-openfoam-domain-pack/plan.md`
   - CFD/OpenFOAM MVP 域包，覆盖四类标准案例。

6. `06-execution-environment-engine/plan.md`
   - 本机 OpenFOAM 优先，Docker/OpenFOAM 兜底，日志和失败诊断。

7. `07-validation-report-delivery/plan.md`
   - 验证证据、报告、交付包、可信度说明。

8. `08-testing-production-readiness/plan.md`
   - 黄金案例、测试、真实 smoke test、发布就绪报告。

9. `09-github-cli-extension/plan.md`
   - GitHub CLI extension 产品入口，命令为 `gh physics-sim`。

## Recommended Execution Order

1. `02-physics-problem-schema`
2. `04-solver-registry-adapters`
3. `01-platform-product-shell`
4. `03-domain-intake-clarification`
5. `05-cfd-openfoam-domain-pack`
6. `06-execution-environment-engine`
7. `07-validation-report-delivery`
8. `08-testing-production-readiness`
9. `09-github-cli-extension`

如果目标是尽快获得用户可运行入口，也可以在 `02`、`04` 和 `01` 后先执行 `09` 的脚手架和 `doctor/init/new/status` mock 流程，再继续接入 CFD/OpenFOAM 真实能力。

## Consolidation Input

未来生成 `consolidation.md` 时，应从每个 plan 收集：

- 已完成能力。
- 未完成能力。
- 偏离 PRD 的地方。
- 新发现的领域边界。
- adapter 扩展风险。
- 测试和验证缺口。
- 下一轮优先做的领域包。
