# Goal 06: Execution Environment And Engine

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/06-execution-environment-engine/plan.md，实现平台执行环境和分阶段执行引擎，MVP 优先检测并使用本机 OpenFOAM，不可用时用 Docker/OpenFOAM 兜底，同时保持未来 solver adapter 可复用。
验证：先读取 PRD、对应 plan、adapter execution plan 契约和 OpenFOAM case 产物；用 mock 命令测试本机 OpenFOAM 检测、Docker 兜底、命令 runner、阶段状态、日志捕获、checkMesh 解析、solver 日志解析和失败诊断；如果本机 OpenFOAM 或 Docker 可用，运行一个最小直管 smoke test；保存测试输出和环境检测结果。
约束：不强制安装 OpenFOAM 或 Docker；不修改系统 shell、Docker daemon、用户镜像库或生产数据；真实执行只在生成的 workspace 内运行；所有失败必须保留原始日志。
边界：只写入 physics-simulation-agent/ 或 cfd-openfoam-agent/ 中 environment detection、command runner、execution orchestration、log parsers、diagnostics、tests 和 fixtures；不要改 case templates 或报告模块，除非接口最小适配。
迭代策略：先实现 mock 可测 runner 和状态机，再加环境检测和 fallback，随后加 OpenFOAM log parser，最后加条件式真实 smoke test；每步跑相关测试；真实环境失败时记录原因而不是修系统。
完成条件：执行引擎能选择 local 或 Docker 模式，能分阶段运行或 mock 运行 case，能捕获日志和错误，能解析关键成功失败信号，测试通过，真实 smoke test 在环境可用时通过或清楚跳过。
暂停条件：需要系统安装权限、拉取大型镜像且未授权、远程集群、生产数据、破坏性命令、修改系统配置，或需要专业 CFD 判断时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement the platform execution environment and staged execution engine from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/06-execution-environment-engine/plan.md, preferring local OpenFOAM for the MVP and falling back to Docker/OpenFOAM when unavailable while remaining reusable for future solver adapters.
Verification: inspect the PRD, matching plan, adapter execution-plan contract, and OpenFOAM case artifacts first; use mocked commands to test local OpenFOAM detection, Docker fallback, command runner, stage status, log capture, checkMesh parsing, solver log parsing, and failure diagnosis; if local OpenFOAM or Docker is available, run one minimal straight-pipe smoke test; save test output and environment detection results.
Constraints: do not force-install OpenFOAM or Docker; do not modify system shell, Docker daemon, user image stores, or production data; real execution must run only inside generated workspaces; all failures must preserve raw logs.
Boundaries: write only environment detection, command runner, execution orchestration, log parsers, diagnostics, tests, and fixtures under physics-simulation-agent/ or cfd-openfoam-agent/; do not modify case templates or report module except for minimal interface adaptation.
Iteration policy: implement a mock-testable runner and state machine first, then environment detection and fallback, then OpenFOAM log parsers, and finally conditional real smoke testing; run related tests after each step; when real environment checks fail, record the reason instead of repairing the system.
Stop when: the engine can select local or Docker mode, run or mock-run a case by stage, capture logs and errors, parse key success and failure signals, pass tests, and either pass a real smoke test when available or clearly skip it.
Pause if: system installation permission, large image pulling without authorization, remote clusters, production data, destructive commands, system configuration changes, or professional CFD judgment is required.
```
