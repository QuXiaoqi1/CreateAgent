# Goal 07: Testing And Production Readiness

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/07-testing-production-readiness/plan.md，为 CFD OpenFOAM Agent 建立生产级 MVP 的测试与发布就绪门槛，覆盖四个黄金案例、schema、输入解析、case 生成、执行引擎、报告打包、环境诊断和失败路径。
验证：先读取 PRD、对应 plan 和当前实现；发现项目已有测试命令、构建命令和运行方式；补齐 fixture、单元测试、集成测试、mock 全流程测试和条件式真实 OpenFOAM smoke test；运行最小完整测试套件；生成或更新 release readiness 检查结果，并保存命令输出。
约束：不为了测试通过而降低 PRD 验收标准；不删除真实日志或 fixture；不强制安装 OpenFOAM、Docker 或外部依赖；不引入生产账号、云服务、付费 API 或大规模数值 benchmark 作为 MVP 必需项。
边界：只写入 cfd-openfoam-agent/ 中测试、fixtures、测试工具、release readiness 检查和必要实现修复，以及 specs/cfd-openfoam-agent/ 中与验收状态直接相关的说明；不要做无关重构或新增产品范围。
迭代策略：先建立四个黄金案例 fixture，再补单元测试，然后补 mock 集成测试，最后加环境可用时的真实 smoke test；每次失败先读测试输出和相关日志；同一失败连续 2 次后缩小到最小复现。
完成条件：核心测试套件能验证四类黄金案例和主要失败路径，缺少真实 OpenFOAM 或 Docker 时能优雅跳过真实 smoke test，release readiness 报告列出通过项、跳过项、风险和下一步，测试输出已记录。
暂停条件：需要真实生产部署、远程集群、付费服务、系统安装权限、大规模计算预算、专业 CFD benchmark 结论，或需要用户决定是否扩大 MVP 质量范围时暂停。
```

## 默认选择理由

最后做统一测试和发布门槛，可以把前六个模块的真实完成度收束成可验证证据，也为 consolidation 提供可靠输入。

## Goal Draft (English-compatible)

```text
/goal Establish the production-grade MVP testing and release readiness gates for the CFD OpenFOAM Agent from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/07-testing-production-readiness/plan.md, covering the four golden cases, schema, input parsing, case generation, execution engine, report packaging, environment diagnostics, and failure paths.
Verification: inspect the PRD, the matching plan, and the current implementation first; discover existing test, build, and run commands; add fixtures, unit tests, integration tests, mocked full-flow tests, and a conditional real OpenFOAM smoke test; run the smallest complete test suite; generate or update release readiness results and save command output.
Constraints: do not lower PRD acceptance standards just to make tests pass; do not delete real logs or fixtures; do not force-install OpenFOAM, Docker, or external dependencies; do not introduce production accounts, cloud services, paid APIs, or large numerical benchmarks as MVP requirements.
Boundaries: write only tests, fixtures, test utilities, release readiness checks, and necessary implementation fixes under cfd-openfoam-agent/, plus directly related acceptance-status notes under specs/cfd-openfoam-agent/; do not perform unrelated refactors or add new product scope.
Iteration policy: build four golden-case fixtures first, then unit tests, then mocked integration tests, and finally a real smoke test when the environment is available; read test output and related logs after each failure; after 2 repeated failures, reduce to the smallest reproduction.
Stop when: the core test suite verifies the four golden cases and major failure paths, real smoke tests skip gracefully when OpenFOAM or Docker is unavailable, the release readiness report lists passed items, skipped items, risks, and next steps, and test output is recorded.
Pause if: real production deployment, remote clusters, paid services, system install permissions, large compute budgets, professional CFD benchmark conclusions, or a user decision to expand the MVP quality scope is required.
```
