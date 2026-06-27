# Goal 02: Physics Problem Schema

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/02-physics-problem-schema/plan.md，建立通用 Physics Problem Schema，支持物理域、控制模型、几何、材料、初始条件、边界条件、网格策略、时间策略、求解策略、后处理目标、假设、来源证据和验证结果。
验证：先读取 PRD、对应 plan 和旧 CFD schema 文档；检查项目已有类型、测试命令和 fixtures；实现或更新 schema、provenance、assumption、validation、domain extension 和 serialization；添加通用 schema、CFD 扩展、缺失单位、默认审批、非 MVP 领域 draft-only 的测试；运行最小相关测试并保存输出。
约束：不生成具体 solver 输入、不运行求解器、不扩大到所有物理场自动求解；未确认默认值、低置信度截图值、缺单位或阻塞错误不得进入 solver adapter。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 schema、types、validation、fixtures、tests 相关文件，以及 specs/physics-simulation-agent/ 中必要说明；不要改执行引擎、报告模块或系统环境。
迭代策略：先定义最小通用 schema，再补 provenance 和 assumptions，随后加入 validation 和 domain extension；每加一层契约就跑对应测试；失败时缩小到最小 schema fixture。
完成条件：通用 schema 能序列化为 problem.schema.json，CFD 扩展可挂载，缺失和歧义输入能返回阻塞问题，非 MVP 领域不会误称可执行，相关测试通过并记录证据。
暂停条件：需要用户决定新增物理域边界、接受未确认默认值、引入外部标准、改变 MVP 范围，或需要专业工程判断时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Build the canonical Physics Problem Schema from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/02-physics-problem-schema/plan.md, covering physics domain, governing model, geometry, materials, initial conditions, boundary conditions, mesh strategy, time strategy, solver strategy, postprocessing targets, assumptions, provenance, and validation results.
Verification: inspect the PRD, matching plan, and previous CFD schema documents first; inspect existing types, test commands, and fixtures; implement or update schema, provenance, assumptions, validation, domain extension, and serialization; add tests for generic schema, CFD extension, missing units, default approval, and non-MVP draft-only domains; run the smallest relevant tests and save output.
Constraints: do not generate solver-specific input, run solvers, or expand to automatic solving for every physics field; unconfirmed defaults, low-confidence screenshot values, missing units, or blocking errors must not enter solver adapters.
Boundaries: write only schema, types, validation, fixtures, and tests under physics-simulation-agent/ or cfd-openfoam-agent/, plus necessary notes under specs/physics-simulation-agent/; do not modify the execution engine, report module, or system environment.
Iteration policy: define the minimal generic schema first, then provenance and assumptions, then validation and domain extension; run related tests after each contract layer; reduce failures to the smallest schema fixture.
Stop when: the generic schema serializes to problem.schema.json, CFD extension attaches cleanly, missing and ambiguous inputs return blocking questions, non-MVP domains do not falsely claim execution, relevant tests pass, and evidence is recorded.
Pause if: the user must decide new physics-domain boundaries, accept unconfirmed defaults, introduce external standards, change MVP scope, or provide professional engineering judgment.
```
