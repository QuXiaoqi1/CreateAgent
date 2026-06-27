# Goal 08: Testing And Production Readiness

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/08-testing-production-readiness/plan.md，为 Physics Simulation Agent 建立生产级 MVP 测试和发布就绪门槛，覆盖四个 CFD 黄金案例、非 MVP draft-only 行为、schema、intake、registry、OpenFOAM case、执行、报告和失败路径。
验证：先读取 PRD、对应 plan 和当前实现；发现项目已有测试、构建和运行命令；补齐 fixtures、单元测试、集成测试、mock 全流程测试和条件式真实 OpenFOAM smoke test；运行最小完整测试套件；生成 release readiness 结果，列出通过、失败、跳过、风险和下一轮建议，并保存命令输出。
约束：不为了测试通过而降低 PRD 验收标准；不删除真实日志或 fixtures；不强制安装 OpenFOAM、Docker 或外部依赖；不把大规模 benchmark、云服务、付费 API 或正式工程认证列为 MVP 必需。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 tests、fixtures、test utilities、release readiness 检查和必要实现修复，以及 specs/physics-simulation-agent/ 中验收状态说明；不要做无关重构或新增产品范围。
迭代策略：先建立黄金案例 fixtures，再补 schema/intake/registry 单元测试，然后补 case/execution/report 集成测试，最后加条件式真实 smoke test；每次失败先读测试输出和日志；同一失败连续 2 次后缩小到最小复现。
完成条件：核心测试能覆盖四个 CFD 黄金案例、非 MVP draft-only、主要失败路径和交付包完整性；缺少 OpenFOAM 或 Docker 时真实 smoke test 能优雅跳过；release readiness 报告清楚列出状态和风险，证据已记录。
暂停条件：需要真实生产部署、远程集群、付费服务、系统安装权限、大规模计算预算、专业 benchmark 结论，或用户决定扩大质量范围时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Establish production-grade MVP testing and release readiness gates for Physics Simulation Agent from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/08-testing-production-readiness/plan.md, covering the four CFD golden cases, non-MVP draft-only behavior, schema, intake, registry, OpenFOAM cases, execution, reporting, and failure paths.
Verification: inspect the PRD, matching plan, and current implementation first; discover existing test, build, and run commands; add fixtures, unit tests, integration tests, mocked full-flow tests, and a conditional real OpenFOAM smoke test; run the smallest complete test suite; generate release readiness results listing pass, fail, skip, risks, and next-round recommendations, and save command output.
Constraints: do not lower PRD acceptance standards just to pass tests; do not delete real logs or fixtures; do not force-install OpenFOAM, Docker, or external dependencies; do not make large benchmarks, cloud services, paid APIs, or formal engineering certification MVP requirements.
Boundaries: write only tests, fixtures, test utilities, release readiness checks, and necessary implementation fixes under physics-simulation-agent/ or cfd-openfoam-agent/, plus acceptance-status notes under specs/physics-simulation-agent/; do not perform unrelated refactors or add new product scope.
Iteration policy: establish golden-case fixtures first, then schema, intake, and registry unit tests, then case, execution, and report integration tests, and finally conditional real smoke testing; read test output and logs after each failure; after 2 repeated failures, reduce to the smallest reproduction.
Stop when: core tests cover the four CFD golden cases, non-MVP draft-only behavior, major failure paths, and package completeness; real smoke tests skip gracefully without OpenFOAM or Docker; release readiness clearly lists status and risks; evidence is recorded.
Pause if: real production deployment, remote clusters, paid services, system install permissions, large compute budgets, professional benchmark conclusions, or a user decision to expand quality scope is required.
```
