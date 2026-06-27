# Goal 04: OpenFOAM Case Generator

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/04-openfoam-case-generator/plan.md，实现模板驱动的 OpenFOAM case 生成器，使已确认 schema 能为二维直管、二维弯管、房间通风、绕流四类 MVP 案例生成可检查的 case 目录、字典文件和可复现运行脚本。
验证：先读取 PRD、对应 plan 和已实现 schema 契约；检查项目测试命令和 OpenFOAM 相关 fixture；为四类案例生成 case snapshot 或结构测试；验证 0、constant、system、blockMeshDict、controlDict、fvSchemes、fvSolution、transportProperties、turbulenceProperties 和 run 脚本存在且关键字段完整；运行最小相关测试并保存输出。
约束：不执行 OpenFOAM 求解、不修改用户系统 OpenFOAM 或 Docker 配置、不支持复杂 CAD 自动修复；无法安全表达的几何必须返回阻塞错误；求解器和模型选择必须记录理由。
边界：只写入 cfd-openfoam-agent/ 中 case 模板、渲染器、solver strategy、OpenFOAM 字典生成、tests 和 fixtures，以及 specs/cfd-openfoam-agent/ 中必要说明；不要改执行引擎、报告模块或本地产品壳，除非接口契约需要最小适配。
迭代策略：先完成直管最小 case，再扩展弯管、房间通风和绕流；每类案例完成后跑结构测试；失败时优先检查 schema 输入、模板渲染和边界命名；最多做 3 轮聚焦改进后列出剩余几何限制。
完成条件：四类 MVP 案例都能从有效 schema 生成确定性的 OpenFOAM case 目录和 run 脚本，结构测试通过，无法表达的输入会阻塞而不是猜测，生成理由和 metadata 已记录。
暂停条件：需要真实复杂 CAD、snappyHexMesh 高级配置、专业网格策略判断、用户接受不明确几何近似，或需要安装和运行系统级 OpenFOAM 时暂停。
```

## 默认选择理由

模板驱动 case 生成能先覆盖四类标准场景，既能快速进入可运行阶段，又能保留后续复杂网格工具扩展空间。

## Goal Draft (English-compatible)

```text
/goal Implement a template-driven OpenFOAM case generator from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/04-openfoam-case-generator/plan.md, so confirmed schemas can generate inspectable case directories, dictionary files, and reproducible run scripts for 2D straight pipe, 2D bent pipe, room ventilation, and flow-around-object MVP cases.
Verification: inspect the PRD, the matching plan, and the implemented schema contract first; inspect project test commands and OpenFOAM fixtures; add case snapshot or structural tests for all four case families; verify 0, constant, system, blockMeshDict, controlDict, fvSchemes, fvSolution, transportProperties, turbulenceProperties, and the run script exist with required fields; run the smallest relevant tests and save output.
Constraints: do not execute OpenFOAM solvers, modify the user's system OpenFOAM installation, or change Docker configuration; do not support complex CAD auto-repair; geometry that cannot be represented safely must return a blocking error; solver and model choices must record rationale.
Boundaries: write only case templates, renderers, solver strategy, OpenFOAM dictionary generation, tests, and fixtures under cfd-openfoam-agent/, plus necessary documentation updates under specs/cfd-openfoam-agent/; do not modify the execution engine, report module, or local product shell except for minimal interface-contract adaptation.
Iteration policy: implement the minimal straight-pipe case first, then expand to bent pipe, room ventilation, and flow around object; run structural tests after each case family; on failure, inspect schema input, template rendering, and boundary naming first; make at most 3 focused improvement rounds before listing remaining geometry limits.
Stop when: all four MVP case families deterministically generate OpenFOAM case directories and run scripts from valid schemas, structural tests pass, unrepresentable inputs block instead of being guessed, and generation rationale plus metadata are recorded.
Pause if: real complex CAD, advanced snappyHexMesh configuration, professional mesh strategy judgment, user approval for unclear geometry approximation, or installing and running system-level OpenFOAM is required.
```
