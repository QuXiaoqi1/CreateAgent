# Goal 05: Execution Environment And Engine

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/05-execution-environment-engine/plan.md，实现 OpenFOAM 执行环境检测和分阶段执行引擎，优先使用用户本机 OpenFOAM，在不可用时用 Docker/OpenFOAM 兜底，并记录每个命令、日志、退出码、耗时和诊断结果。
验证：先读取 PRD、对应 plan 和已生成 case 契约；检查项目测试命令和环境；用 mock 命令测试本机 OpenFOAM 检测、Docker 兜底、命令日志、阶段状态、checkMesh 解析、solver 日志解析和失败诊断；如果本机 OpenFOAM 或 Docker 可用，再运行一个最小直管 smoke test；保存测试输出和环境检测结果。
约束：不强制安装 OpenFOAM 或 Docker；不修改系统 shell 配置、Docker daemon、用户镜像库或生产数据；真实求解只在用户工作区生成的 case 内执行；所有失败必须保留原始日志。
边界：只写入 cfd-openfoam-agent/ 中环境检测、命令 runner、执行编排、日志解析、诊断、tests 和 fixtures，以及 specs/cfd-openfoam-agent/ 中必要说明；不要改 case 模板或报告模块，除非为接口契约做最小适配。
迭代策略：先实现 mock 可测的命令 runner 和状态机，再加环境检测，再加 checkMesh 和 solver 解析，最后加真实 smoke test 的条件执行；每步跑相关测试；真实环境失败时先记录环境信息，不做系统级修复。
完成条件：执行引擎能选择本机或 Docker 模式，能分阶段运行或 mock 运行 case，能捕获日志和错误，能解析关键成功失败信号，相关测试通过，真实 smoke test 在环境可用时通过或给出清晰跳过原因。
暂停条件：需要安装系统软件、拉取大型镜像且用户未授权、访问远程集群、使用生产数据、修改系统配置、执行破坏性命令，或 OpenFOAM 错误需要专业 CFD 判断时暂停。
```

## 默认选择理由

先把执行环境和日志诊断做稳，才能让非专业用户知道失败发生在哪里，也能支撑后续报告和迭代修复。

## Goal Draft (English-compatible)

```text
/goal Implement OpenFOAM environment detection and a staged execution engine from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/05-execution-environment-engine/plan.md, preferring the user's local OpenFOAM installation and falling back to Docker/OpenFOAM when unavailable, while recording every command, log, exit code, duration, and diagnosis.
Verification: inspect the PRD, the matching plan, and the generated case contract first; inspect project test commands and the environment; use mocked commands to test local OpenFOAM detection, Docker fallback, command logging, stage status, checkMesh parsing, solver log parsing, and failure diagnosis; if local OpenFOAM or Docker is available, run one minimal straight-pipe smoke test; save test output and environment detection results.
Constraints: do not force-install OpenFOAM or Docker; do not modify system shell configuration, Docker daemon settings, user image stores, or production data; real solving must run only inside generated cases in the user workspace; all failures must preserve raw logs.
Boundaries: write only environment detection, command runner, execution orchestration, log parsing, diagnosis, tests, and fixtures under cfd-openfoam-agent/, plus necessary documentation updates under specs/cfd-openfoam-agent/; do not modify case templates or the report module except for minimal interface-contract adaptation.
Iteration policy: implement the mock-testable command runner and state machine first, then environment detection, then checkMesh and solver parsing, and finally conditional real smoke testing; run related tests after each step; when real environment checks fail, record environment facts instead of making system-level fixes.
Stop when: the execution engine can select local or Docker mode, run or mock-run a case by stage, capture logs and errors, parse key success and failure signals, pass relevant tests, and either pass a real smoke test when available or clearly explain why it was skipped.
Pause if: system software installation, large image pulling without user permission, remote cluster access, production data, system configuration changes, destructive commands, or professional CFD judgment about OpenFOAM errors is required.
```
