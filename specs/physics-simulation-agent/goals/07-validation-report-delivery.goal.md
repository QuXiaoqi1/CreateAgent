# Goal 07: Validation, Report, And Delivery

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/07-validation-report-delivery/plan.md，实现验证证据、报告和交付包生成，让模拟任务输出 runnable status、收敛状态、基础 sanity check、假设、限制、可信度和复现说明。
验证：先读取 PRD、对应 plan、schema、执行日志和 CFD domain pack 产物契约；使用 fixture 日志和结果测试验证证据模型、OpenFOAM MVP 指标、语言选择、report.md 和 package builder；确认交付包包含 README、problem.schema.json、assumptions、solver-input、run 脚本、logs、results、report、metadata；运行最小相关测试并保存输出。
约束：不声称正式工程认证或绝对准确；不隐藏失败、假设或限制；不把可运行等同于可信；不把 ParaView 自动截图作为 MVP 必需项；不使用外部付费翻译或文档服务，除非用户授权。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 validation evidence、postprocessing、report generator、package builder、tests 和 fixtures，以及 specs/physics-simulation-agent/ 必要说明；不要改 schema、case generator 或执行引擎，除非读取产物需要最小适配。
迭代策略：先实现交付包结构，再实现报告，然后补 validation evidence 和 CFD 指标；每加入一类结果解析就跑 fixture 测试；报告用非专家可理解语言解释，技术细节放附录或引用文件。
完成条件：成功和失败 fixture 都能生成交付包，报告包含目标、输入、假设、求解设置、环境、网格、收敛、sanity check、结果、限制、可信度和复现说明，测试通过并记录证据。
暂停条件：需要企业或学校固定模板、正式工程结论背书、复杂可视化、版权素材、外部翻译服务、缺失关键结果文件，或用户改变报告语言策略时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement validation evidence, report generation, and delivery packaging from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/07-validation-report-delivery/plan.md, so simulation tasks output runnable status, convergence status, basic sanity checks, assumptions, limitations, confidence, and reproduction instructions.
Verification: inspect the PRD, matching plan, schema, execution log contract, and CFD domain-pack artifact contract first; use fixture logs and results to test validation evidence model, OpenFOAM MVP metrics, language selection, report.md, and package builder; verify the package contains README, problem.schema.json, assumptions, solver-input, run script, logs, results, report, and metadata; run the smallest relevant tests and save output.
Constraints: do not claim formal engineering certification or absolute accuracy; do not hide failures, assumptions, or limitations; do not equate runnable with trustworthy; do not require ParaView screenshot automation for MVP; do not use paid external translation or document services unless authorized.
Boundaries: write only validation evidence, postprocessing, report generator, package builder, tests, and fixtures under physics-simulation-agent/ or cfd-openfoam-agent/, plus necessary notes under specs/physics-simulation-agent/; do not modify schema, case generator, or execution engine except for minimal output-reading adaptation.
Iteration policy: implement delivery package structure first, then report generation, then validation evidence and CFD metrics; run fixture tests after each parser; explain reports in non-expert language and keep technical detail in appendices or referenced files.
Stop when: success and failure fixtures can generate delivery packages, reports include objective, inputs, assumptions, solver setup, environment, mesh, convergence, sanity checks, results, limitations, confidence, and reproduction instructions, tests pass, and evidence is recorded.
Pause if: fixed enterprise or school templates, formal engineering sign-off, complex visualization, copyrighted assets, external translation services, missing critical result files, or a user decision to change report language behavior is required.
```
