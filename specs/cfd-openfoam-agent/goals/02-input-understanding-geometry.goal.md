# Goal 02: Input Understanding And Geometry Reconstruction

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/02-input-understanding-geometry/plan.md，实现输入理解与简化几何重建能力，把自然语言、截图提取结果、CSV/XLSX 和粘贴表格转成可追溯的 CFD 问题草案，并在数据明确时生成四类 MVP 案例的几何草案。
验证：先读取 PRD 和对应 plan，检查当前工程已有解析、测试和 fixture；为二维直管、二维弯管、房间通风、绕流各准备至少一个输入 fixture；运行解析和几何完整性测试；证明明确数据能生成几何草案，模糊数据会产生用户澄清问题，并保存测试输出作为证据。
约束：不从任意复杂图片臆造高保真 CAD；截图提取值必须带置信度和确认状态；不使用外部付费 OCR 或 LLM 服务，除非用户明确提供凭证并允许；不把低置信度数据直接用于求解。
边界：只写入 cfd-openfoam-agent/ 中输入解析、单位归一、证据映射、几何草案、澄清问题相关代码，以及 specs/cfd-openfoam-agent/ 下直接相关测试 fixture；不要修改 case 生成器、执行引擎或报告模块，除非为接口契约做最小调整。
迭代策略：先定义输入 artifact 和证据模型，再实现自然语言、表格、截图 mock 输出解析，最后做四类几何完整性判断；每个输入类型完成后跑对应测试；连续失败 2 次后缩小到最小 fixture 复现。
完成条件：系统能从代表性输入生成带来源证据的 CFD 问题草案，能对明确几何生成草案，能对缺失或歧义几何提出澄清问题，相关测试通过并记录证据。
暂停条件：需要真实付费 OCR、外部模型密钥、复杂 CAD 重建、CFD 专家判断、无法确定的几何拓扑，或用户必须补充尺寸和边界含义时暂停。
```

## 默认选择理由

先实现可追溯的输入草案和简化几何判断，比直接追求复杂 CAD 重建更稳，也更符合 MVP 的四类标准案例。

## Goal Draft (English-compatible)

```text
/goal Implement input understanding and simplified geometry reconstruction from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/02-input-understanding-geometry/plan.md, converting natural language, screenshot extraction results, CSV/XLSX files, and pasted tables into traceable CFD problem drafts, and producing geometry drafts for the four MVP case families when the data is explicit.
Verification: inspect the PRD, the matching plan, and existing parsing tests and fixtures first; prepare at least one input fixture each for 2D straight pipe, 2D bent pipe, room ventilation, and flow around object; run parsing and geometry completeness tests; prove explicit data produces geometry drafts while ambiguous data produces user clarification questions, saving test output as evidence.
Constraints: do not invent high-fidelity CAD from arbitrary complex images; screenshot-derived values must include confidence and confirmation state; do not use paid external OCR or LLM services unless the user explicitly provides credentials and permission; do not send low-confidence values directly to solving.
Boundaries: write only input parsing, unit normalization, evidence mapping, geometry draft, and clarification-question code under cfd-openfoam-agent/, plus directly related test fixtures under specs/cfd-openfoam-agent/; do not modify the case generator, execution engine, or report module except for minimal interface-contract adjustments.
Iteration policy: define the input artifact and evidence model first, then implement natural-language, table, and mocked screenshot-output parsing, then add completeness checks for the four geometry families; rerun the relevant tests after each input type; after 2 repeated failures, reduce to the smallest fixture reproduction.
Stop when: the system can produce a source-traceable CFD problem draft from representative inputs, generate geometry drafts from explicit geometry, ask clarification questions for missing or ambiguous geometry, pass relevant tests, and record evidence.
Pause if: real paid OCR, external model credentials, complex CAD reconstruction, CFD expert judgment, uncertain geometry topology, or user-supplied missing dimensions and boundary meanings are required.
```
