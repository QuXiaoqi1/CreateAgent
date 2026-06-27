# Goal 01: Platform Product Shell

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/01-platform-product-shell/plan.md，实现 Physics Simulation Agent 的本地优先平台产品壳，让用户能创建模拟任务、登记输入、查看阶段、回答 checkpoint，并通过统一 workflow controller 承接未来 CLI 和 Web 适配。
验证：先读取 PRD 和对应 plan，检查当前项目结构与可用命令；如果还没有实现工程，在 cfd-openfoam-agent/ 或新建的 physics-simulation-agent/ 下创建最小本地工程骨架；运行项目发现到的最小测试或新增本地测试；用一个 mock 物理模拟任务从创建、输入登记、checkpoint 到交付入口走通，并保存日志或命令输出。
约束：不加入云端账号、团队权限、生产部署、付费服务、复杂桌面打包或无关功能；不绑定单一 solver；不要求非专家直接编辑求解器输入文件。
边界：只写入 physics-simulation-agent/、cfd-openfoam-agent/ 中平台壳相关代码、测试和 fixtures，以及 specs/physics-simulation-agent/ 中必要说明；不要修改系统 OpenFOAM、Docker 配置、用户私有文件或无关目录。
迭代策略：先完成 workspace、task state、artifact registry、checkpoint 和 workflow controller 的最小闭环；每完成一个子模块就运行相关检查；失败时先读取状态文件和日志；最多做 3 轮聚焦改进后报告剩余风险。
完成条件：平台壳能本地创建任务、登记输入、暂停等待用户确认、记录 artifact、暴露交付入口，测试通过或明确说明缺失环境，且运行证据已记录。
暂停条件：需要用户决定具体 UI 技术栈、外部账号、生产数据、付费 API、系统级安装、破坏性操作或访问私密文件时暂停。
```

## Goal Draft (English-compatible)

```text
/goal Implement the local-first platform product shell for Physics Simulation Agent from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/01-platform-product-shell/plan.md, so users can create simulation tasks, register inputs, view stages, answer checkpoints, and use a shared workflow controller ready for future CLI and Web adapters.
Verification: inspect the PRD, matching plan, project structure, and available commands first; if no implementation project exists, create a minimal local project under cfd-openfoam-agent/ or physics-simulation-agent/; run the smallest discovered or newly added local tests; complete one mocked physical simulation task from creation through input registration and checkpoint to delivery entry, saving logs or command output.
Constraints: do not add cloud accounts, team permissions, production deployment, paid services, complex desktop packaging, or unrelated features; do not bind the platform to one solver; do not require non-experts to edit solver input files directly.
Boundaries: write only platform-shell code, tests, and fixtures under physics-simulation-agent/ or cfd-openfoam-agent/, plus necessary notes under specs/physics-simulation-agent/; do not modify system OpenFOAM, Docker configuration, private user files, or unrelated directories.
Iteration policy: build the smallest loop for workspace, task state, artifact registry, checkpoints, and workflow controller first; run relevant checks after each submodule; inspect state files and logs before changing strategy; make at most 3 focused improvement rounds before reporting remaining risks.
Stop when: the shell can create a local task, register inputs, pause for confirmation, record artifacts, expose a delivery entry, pass tests or report missing environment, and record runtime evidence.
Pause if: the user must decide the exact UI stack, external accounts, production data, paid APIs, system installation, destructive operations, or private-file access is required.
```
