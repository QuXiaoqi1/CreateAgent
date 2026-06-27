# CFD OpenFOAM Agent Plans

本目录由 PRD 拆分而来，用于第 2 步的多计划开发。每个子目录包含一个独立 `plan.md`，后续第 3 步会基于这些计划生成 `/goal` 提示词。

## Plan List

1. `01-local-product-shell/plan.md`
   - 本地优先产品壳、任务工作区、状态、输入登记、用户确认、交付包入口。

2. `02-input-understanding-geometry/plan.md`
   - 自然语言、截图、表格解析，以及基于明确数据的简化几何重建。

3. `03-cfd-problem-schema/plan.md`
   - CFD 结构化问题定义、单位、假设、默认值、确认和能力边界。

4. `04-openfoam-case-generator/plan.md`
   - 四类标准案例的 OpenFOAM case 生成、字典渲染、运行脚本。

5. `05-execution-environment-engine/plan.md`
   - 本机 OpenFOAM 优先、Docker/OpenFOAM 兜底、命令编排、日志和失败诊断。

6. `06-postprocessing-report/plan.md`
   - 后处理、关键指标、双语报告和完整交付包。

7. `07-testing-production-readiness/plan.md`
   - 测试覆盖、黄金案例、环境诊断、发布检查和生产级质量门槛。

## Suggested Execution Order

1. 先执行 `03-cfd-problem-schema`，建立所有模块的共享契约。
2. 并行推进 `01-local-product-shell` 和 `02-input-understanding-geometry`。
3. 在 schema 稳定后执行 `04-openfoam-case-generator`。
4. case 生成可用后执行 `05-execution-environment-engine`。
5. 有执行产物后执行 `06-postprocessing-report`。
6. 最后用 `07-testing-production-readiness` 串起测试、验收和发布检查。

## Consolidation Input

第 5 步生成 `consolidation.md` 时，应从每个 `plan.md` 收集：

- 已完成能力。
- 未完成能力。
- 偏离 PRD 的地方。
- 新发现风险。
- 用户体验缺口。
- 测试缺口。
- 下一轮需要补的功能。
