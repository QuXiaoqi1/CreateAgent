# Goal 03: Domain Intake And Clarification

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/03-domain-intake-clarification/plan.md，实现物理模拟输入理解、领域识别和澄清问题生成，把自然语言、截图提取结果、CSV/XLSX 和粘贴表格转成 Physics Problem Schema 草案。
验证：先读取 PRD、对应 plan 和 schema 契约；准备 CFD、热传导、结构、PDE、多体动力学、多物理场、未知领域的输入 fixtures；运行领域分类、表格解析、单位归一、schema draft、澄清问题测试；证明 MVP CFD 输入可继续求解，非 MVP 输入只生成结构化草案并明确暂不支持自动求解。
约束：不从复杂图片臆造高保真 CAD；不使用付费 OCR 或外部模型密钥，除非用户明确授权；不把非 MVP 领域包装成已支持求解；截图提取值必须带确认状态。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 intake、domain classification、unit normalization、schema draft、clarification、fixtures 和 tests；不要改 solver adapter、执行引擎或报告模块，除非接口契约需要最小适配。
迭代策略：先实现领域分类，再实现表格和文本解析，随后做 schema draft 和 clarification；每类输入完成后跑对应测试；同一失败连续 2 次后缩小到最小 fixture。
完成条件：系统能分类主要物理领域，能为 MVP CFD 生成可验证草案，能为非 MVP 领域生成 draft-only 状态，能对缺失参数提出澄清问题，测试通过并保存证据。
暂停条件：需要真实外部 OCR、复杂 CAD 重建、用户补充关键尺寸或边界含义、专业领域判断、外部模型密钥或扩大自动求解范围时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement physical simulation input understanding, domain classification, and clarification generation from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/03-domain-intake-clarification/plan.md, converting natural language, screenshot extraction results, CSV/XLSX files, and pasted tables into Physics Problem Schema drafts.
Verification: inspect the PRD, matching plan, and schema contract first; prepare input fixtures for CFD, heat transfer, solid mechanics, PDE, multibody dynamics, multiphysics, and unknown domains; run tests for domain classification, table parsing, unit normalization, schema drafting, and clarification questions; prove MVP CFD inputs can continue toward solving while non-MVP inputs produce structured draft-only status with clear unsupported solving messaging.
Constraints: do not invent high-fidelity CAD from complex images; do not use paid OCR or external model credentials unless explicitly authorized; do not present non-MVP domains as automatically solvable; screenshot-derived values must carry confirmation state.
Boundaries: write only intake, domain classification, unit normalization, schema draft, clarification, fixtures, and tests under physics-simulation-agent/ or cfd-openfoam-agent/; do not modify solver adapters, execution engine, or report module except for minimal interface-contract adaptation.
Iteration policy: implement domain classification first, then table and text parsing, then schema drafting and clarification; run related tests after each input type; after 2 repeated failures, reduce to the smallest fixture.
Stop when: the system classifies major physics domains, creates verifiable MVP CFD drafts, creates draft-only status for non-MVP domains, asks clarification questions for missing parameters, passes tests, and saves evidence.
Pause if: real external OCR, complex CAD reconstruction, user-supplied key dimensions or boundary meanings, professional domain judgment, external model credentials, or expanded automatic-solving scope is required.
```
