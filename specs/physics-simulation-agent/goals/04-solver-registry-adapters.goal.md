# Goal 04: Solver Registry And Adapter Interfaces

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/04-solver-registry-adapters/plan.md，实现 solver registry、domain pack 元数据和 solver adapter 接口，使平台能选择 OpenFOAMAdapter，并为未来 FEniCSx、MOOSE、Chrono 等适配器保留清晰扩展点。
验证：先读取 PRD、对应 plan 和 schema 契约；实现 adapter interface、domain pack metadata、capability result、registry 和 OpenFOAMAdapter 注册壳；添加测试验证 CFD/OpenFOAM 能被选择，热传导/结构/PDE/多体等未实现领域返回 draft-only 或 unsupported，不出现虚假支持；运行最小相关测试并保存输出。
约束：不实现完整 FEniCSx、MOOSE、Chrono；不生成复杂 solver 输入；不执行求解器；不对未来 adapter 做已支持承诺；所有选择必须记录理由和限制。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 registry、adapter interface、domain pack metadata、capability tests 和必要 fixtures；不要改 OpenFOAM case 模板、执行引擎或报告模块，除非为接口对接做最小改动。
迭代策略：先定义 adapter 最小接口，再实现 registry，随后接入 OpenFOAMAdapter 壳和 unsupported future adapter metadata；每完成一个接口层就跑测试；失败时从 capability result 入手定位。
完成条件：registry 能根据 schema 选择 OpenFOAMAdapter，能拒绝或 draft-only 处理未实现领域，能输出选择理由、限制和 human-review 状态，测试通过并有证据。
暂停条件：需要实现新 solver、引入外部框架安装、决定 FEniCSx/MOOSE/Chrono 优先级、修改 MVP 领域范围，或需要专业求解器适配判断时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement solver registry, domain pack metadata, and solver adapter interfaces from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/04-solver-registry-adapters/plan.md, enabling the platform to select OpenFOAMAdapter while preserving clear extension points for future FEniCSx, MOOSE, Chrono, and other adapters.
Verification: inspect the PRD, matching plan, and schema contract first; implement adapter interface, domain pack metadata, capability result, registry, and an OpenFOAMAdapter registration shell; add tests proving CFD/OpenFOAM can be selected while heat, solid, PDE, and multibody unimplemented domains return draft-only or unsupported status without false support; run the smallest relevant tests and save output.
Constraints: do not implement full FEniCSx, MOOSE, or Chrono support; do not generate complex solver inputs; do not execute solvers; do not promise future adapters are supported; every selection must record rationale and limitations.
Boundaries: write only registry, adapter interface, domain pack metadata, capability tests, and necessary fixtures under physics-simulation-agent/ or cfd-openfoam-agent/; do not modify OpenFOAM case templates, execution engine, or report module except for minimal interface wiring.
Iteration policy: define the minimal adapter interface first, then implement registry, then wire the OpenFOAMAdapter shell and unsupported future-adapter metadata; run tests after each interface layer; debug from capability result when selection fails.
Stop when: the registry selects OpenFOAMAdapter from schema, rejects or draft-only handles unimplemented domains, outputs rationale, limitations, and human-review status, passes tests, and records evidence.
Pause if: implementing a new solver, installing external frameworks, deciding FEniCSx/MOOSE/Chrono priority, changing MVP domain scope, or professional solver-adapter judgment is required.
```
