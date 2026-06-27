# CFD OpenFOAM Agent Goal Prompts

本目录是第 3 步产物：基于乔木老师的 qiaomu-goal-meta-skill，将每个 plan.md 转成可复制的 Codex `/goal` 指令。

## 推荐执行顺序

1. 03-cfd-problem-schema.goal.md
2. 01-local-product-shell.goal.md
3. 02-input-understanding-geometry.goal.md
4. 04-openfoam-case-generator.goal.md
5. 05-execution-environment-engine.goal.md
6. 06-postprocessing-report.goal.md
7. 07-testing-production-readiness.goal.md

## 使用方式

优先复制每个文件中的“推荐执行版（中文，可直接复制）”代码块到 Codex 目标模式。

先执行 schema 目标，是因为它定义所有模块共享的数据契约。之后再实现产品壳、输入理解、case 生成、执行、报告和测试收束。

## 第 4 步建议

目标模式不要一次塞入全部七个目标。建议一次执行一个目标，完成后记录结果，再进入下一个目标。这样第 5 步生成 consolidation.md 时，可以更准确地判断完成项、遗漏项和下一轮补齐内容。
