# Goal 05: CFD OpenFOAM Domain Pack

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/05-cfd-openfoam-domain-pack/plan.md，实现 MVP 的 domain-pack-cfd-openfoam，使已验证的 CFD schema 能为二维直管、二维弯管、房间通风和绕流生成 OpenFOAM case、运行脚本和 generation manifest。
验证：先读取 PRD、对应 plan、schema 和 adapter 契约；添加四类黄金案例 fixtures；生成并检查 0、constant、system、blockMeshDict、controlDict、fvSchemes、fvSolution、transportProperties、turbulenceProperties、run 脚本和 manifest；运行 case generation 结构测试或 snapshot 测试并保存输出。
约束：不运行 OpenFOAM 求解、不修改系统 OpenFOAM 或 Docker、不实现复杂 CAD、燃烧、复杂多相或强耦合多物理；无法安全表达的几何必须返回阻塞错误；求解器选择必须写入理由。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 CFD domain pack、OpenFOAM adapter、case templates、case generators、tests 和 fixtures，以及 specs/physics-simulation-agent/ 必要说明；不要改执行引擎和报告模块，除非接口最小适配。
迭代策略：先做直管最小 case，再扩展弯管、房间通风、绕流；每完成一个 case family 跑结构测试；失败时检查 schema 输入、边界命名和模板渲染；最多 3 轮聚焦改进后列出几何限制。
完成条件：四类 MVP CFD 案例都能从有效 schema 生成确定性 OpenFOAM case 和 run 脚本，无法表达的输入会阻塞，metadata 和 manifest 完整，测试通过并记录证据。
暂停条件：需要真实复杂 CAD、snappyHexMesh 高级配置、专业网格策略、系统级安装、用户接受不明确几何近似，或扩大 CFD 物理范围时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement the MVP domain-pack-cfd-openfoam from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/05-cfd-openfoam-domain-pack/plan.md, so validated CFD schemas generate OpenFOAM cases, run scripts, and generation manifests for 2D straight pipe, 2D bent pipe, room ventilation, and flow around object.
Verification: inspect the PRD, matching plan, schema contract, and adapter contract first; add fixtures for the four golden cases; generate and verify 0, constant, system, blockMeshDict, controlDict, fvSchemes, fvSolution, transportProperties, turbulenceProperties, run script, and manifest; run case-generation structural or snapshot tests and save output.
Constraints: do not run OpenFOAM solvers, modify system OpenFOAM or Docker, or implement complex CAD, combustion, complex multiphase flow, or strongly coupled multiphysics; geometry that cannot be represented safely must return a blocking error; solver choice must record rationale.
Boundaries: write only CFD domain pack, OpenFOAM adapter, case templates, case generators, tests, and fixtures under physics-simulation-agent/ or cfd-openfoam-agent/, plus necessary notes under specs/physics-simulation-agent/; do not modify execution engine or report module except for minimal interface adaptation.
Iteration policy: implement the minimal straight-pipe case first, then bent pipe, room ventilation, and flow around object; run structural tests after each case family; inspect schema input, boundary naming, and template rendering when failures occur; make at most 3 focused improvement rounds before listing geometry limits.
Stop when: all four MVP CFD cases generate deterministic OpenFOAM cases and run scripts from valid schemas, unrepresentable inputs block, metadata and manifest are complete, tests pass, and evidence is recorded.
Pause if: real complex CAD, advanced snappyHexMesh configuration, professional mesh strategy, system-level installation, user approval for unclear geometry approximation, or expanded CFD physics scope is required.
```
