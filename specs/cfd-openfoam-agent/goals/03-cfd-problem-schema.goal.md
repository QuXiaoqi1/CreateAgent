# Goal 03: CFD Problem Schema And Validation

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/03-cfd-problem-schema/plan.md，建立 CFD OpenFOAM Agent 的规范化问题 schema 与验证层，确保二维直管、二维弯管、房间通风、绕流四类 MVP 案例在进入 OpenFOAM case 生成前都有完整、可追溯、已确认的结构化定义。
验证：先读取 PRD 和对应 plan，检查项目现有类型、schema、测试命令和 fixture；实现或更新 schema、验证器、假设记录、默认值审批和能力边界检查；为四类 MVP 案例添加有效、缺失、歧义、超范围测试；运行最小相关测试并保存输出。
约束：不生成 OpenFOAM 文件、不执行求解器、不做 UI 扩展；不允许未确认的默认值、低置信度截图值或缺失单位直接进入 case 生成；不扩大 MVP 到多相流、燃烧、复杂 CAD 或强耦合多物理。
边界：只写入 cfd-openfoam-agent/ 中 schema、validation、types、fixtures、tests 相关文件，以及 specs/cfd-openfoam-agent/ 中必要的说明更新；不要改动执行引擎、报告模块或系统环境。
迭代策略：先定义最小 schema 契约，再加四类案例的必填字段规则，然后实现假设和来源追踪，最后加超范围拒绝；每加一类规则就跑对应测试；失败时用最小 schema fixture 定位。
完成条件：所有四类 MVP 案例都有通过验证的正向 fixture，缺失和歧义输入能返回阻塞问题，超范围物理能进入人工审查路径，测试通过并留下验证证据。
暂停条件：需要用户决定新增物理模型、改变 MVP 案例边界、接受未确认默认值、引入外部 CFD 标准，或需要专业工程判定时暂停。
```

## 默认选择理由

schema 是所有后续模块的共同契约，先做它能减少 case 生成、执行和报告阶段的返工。

## Goal Draft (English-compatible)

```text
/goal Build the canonical CFD problem schema and validation layer from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/03-cfd-problem-schema/plan.md, ensuring the 2D straight pipe, 2D bent pipe, room ventilation, and flow-around-object MVP cases have complete, traceable, confirmed structured definitions before OpenFOAM case generation.
Verification: inspect the PRD, the matching plan, existing types, schemas, test commands, and fixtures first; implement or update schema, validators, assumption records, default approval, and capability boundary checks; add valid, missing, ambiguous, and out-of-scope tests for all four MVP cases; run the smallest relevant tests and save output.
Constraints: do not generate OpenFOAM files, execute solvers, or expand UI; do not allow unconfirmed defaults, low-confidence screenshot values, or missing units into case generation; do not expand MVP scope to multiphase flow, combustion, complex CAD, or strongly coupled multiphysics.
Boundaries: write only schema, validation, types, fixtures, and tests under cfd-openfoam-agent/, plus necessary documentation updates under specs/cfd-openfoam-agent/; do not modify the execution engine, report module, or system environment.
Iteration policy: define the minimal schema contract first, add required-field rules for the four case families, then implement assumption and provenance tracking, and finally add out-of-scope rejection; rerun related tests after each rule group; use minimal schema fixtures to debug failures.
Stop when: all four MVP case families have passing valid fixtures, missing and ambiguous inputs return blocking questions, out-of-scope physics enters a human-review path, tests pass, and verification evidence is recorded.
Pause if: the user must decide on new physics models, change MVP case boundaries, accept unconfirmed defaults, introduce external CFD standards, or provide professional engineering judgment.
```
