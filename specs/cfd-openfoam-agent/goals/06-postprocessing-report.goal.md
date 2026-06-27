# Goal 06: Postprocessing, Report, And Delivery Package

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/06-postprocessing-report/plan.md，实现后处理、分析报告和完整交付包生成，使一次完成或 mock 完成的 OpenFOAM 任务能输出结果摘要、假设、日志、metadata、可复现说明和面向非 CFD 用户的中英双语报告。
验证：先读取 PRD、对应 plan、schema 和执行日志契约；使用 fixture 日志和结果数据测试残差摘要、网格质量摘要、四类案例关键指标、语言选择、report.md 生成和交付包组装；运行最小相关测试；检查交付包包含 README、assumptions、case、run 脚本、logs、results、report 和 metadata；保存测试输出。
约束：不声称工程认证或绝对准确；不隐藏假设、限制和失败状态；不依赖 ParaView 自动截图作为 MVP 必需项；不使用外部付费文档或翻译服务，除非用户明确授权。
边界：只写入 cfd-openfoam-agent/ 中后处理、指标提取、报告生成、打包、tests 和 fixtures，以及 specs/cfd-openfoam-agent/ 中必要说明；不要改 schema、case 生成器或执行引擎，除非为读取其产物做最小接口适配。
迭代策略：先生成可复现交付目录，再生成 report.md，随后补四类案例指标和双语语言策略；每加一类结果解析就跑 fixture 测试；报告内容用用户可理解语言解释，不用堆砌术语。
完成条件：fixture 和至少一个完整任务产物能生成交付包，报告包含问题摘要、输入假设、求解设置、环境、网格、收敛、关键结果、限制和复现说明，测试通过并记录证据。
暂停条件：需要企业或学校固定报告模板、正式工程结论背书、复杂可视化、版权素材、外部翻译服务、缺失结果文件，或用户要求改变报告语言策略时暂停。
```

## 默认选择理由

报告和交付包是非专业用户真正消费结果的地方，先保证可复现和可解释，比追求复杂可视化更重要。

## Goal Draft (English-compatible)

```text
/goal Implement postprocessing, analysis report generation, and complete delivery packaging from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/06-postprocessing-report/plan.md, so a completed or mocked OpenFOAM task outputs result summaries, assumptions, logs, metadata, reproduction instructions, and a Chinese plus English report for non-CFD users.
Verification: inspect the PRD, the matching plan, schema contracts, and execution log contracts first; use fixture logs and result data to test residual summaries, mesh quality summaries, four case-family metrics, language selection, report.md generation, and package assembly; run the smallest relevant tests; verify the package contains README, assumptions, case, run script, logs, results, report, and metadata; save test output.
Constraints: do not claim engineering certification or absolute accuracy; do not hide assumptions, limitations, or failure states; do not require ParaView screenshot automation for MVP; do not use paid external document or translation services unless the user explicitly authorizes them.
Boundaries: write only postprocessing, metric extraction, report generation, packaging, tests, and fixtures under cfd-openfoam-agent/, plus necessary documentation updates under specs/cfd-openfoam-agent/; do not modify schema, case generator, or execution engine except for minimal interfaces needed to read their outputs.
Iteration policy: generate the reproducible delivery directory first, then report.md, then add four case-family metrics and bilingual language behavior; run fixture tests after each result parser; explain report content in user-facing language instead of piling up CFD terms.
Stop when: fixtures and at least one complete task artifact can generate a delivery package, the report includes problem summary, inputs, assumptions, solver setup, environment, mesh, convergence, key results, limitations, and reproduction instructions, tests pass, and evidence is recorded.
Pause if: a fixed enterprise or school report template, formal engineering sign-off, complex visualization, copyrighted assets, external translation services, missing result files, or a user decision to change report language behavior is required.
```
