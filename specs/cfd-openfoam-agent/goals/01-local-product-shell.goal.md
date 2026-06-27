# Goal 01: Local Product Shell

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/cfd-openfoam-agent/PRD.md 和 specs/cfd-openfoam-agent/plans/01-local-product-shell/plan.md，为 CFD OpenFOAM Agent 创建第一版本地产品壳，使用户能在本地创建仿真任务、登记自然语言和文件输入、查看任务阶段、回答确认问题，并打开最终交付包入口。
验证：先读取 PRD 和对应 plan，检查当前项目结构和可用命令；如果还没有实现工程，在 cfd-openfoam-agent/ 下创建最小本地工程骨架；运行项目发现到的最小测试或新增的本地测试；用一个模拟任务从创建、输入登记、确认检查点到交付包入口走通，并保存命令输出或日志作为证据。
约束：不实现云端账号、团队协作、付费服务、生产部署、复杂桌面打包或无关功能；不要求用户直接编辑 OpenFOAM 字典；保留后续 CLI 和 Web 架构扩展空间。
边界：只写入 cfd-openfoam-agent/、specs/cfd-openfoam-agent/ 中与本地产品壳直接相关的文件、测试和 fixtures；不要修改无关目录、用户私有文件、系统 OpenFOAM 安装或 Docker 配置。
迭代策略：先完成任务工作区、状态模型、输入登记、确认检查点和交付包入口的最小闭环；每完成一个阶段重跑相关检查；失败时先读日志和状态文件再调整；最多做 3 轮聚焦改进后报告剩余风险。
完成条件：本地任务壳能创建任务、登记输入、暂停等待确认、记录状态、暴露交付包入口，相关测试通过或明确说明缺失环境，且产物路径和运行证据已记录。
暂停条件：需要外部账号、真实生产数据、付费 API、破坏性文件操作、用户私密资料、系统级安装修改，或需要用户决定具体 UI 技术栈时暂停。
```

## 默认选择理由

先做本地产品壳，因为它能最快验证非 CFD 用户的核心操作闭环，同时避免云端账号和部署流程拖慢 MVP。

## Goal Draft (English-compatible)

```text
/goal Create the first local product shell for the CFD OpenFOAM Agent from specs/cfd-openfoam-agent/PRD.md and specs/cfd-openfoam-agent/plans/01-local-product-shell/plan.md, so a user can create a local simulation task, register natural-language and file inputs, view task stages, answer confirmation checkpoints, and open the final delivery package entry point.
Verification: inspect the PRD, the matching plan, the current project structure, and available commands first; if no implementation project exists, create a minimal local project under cfd-openfoam-agent/; run the smallest discovered or newly added local tests; complete one mocked task flow from creation through input registration and confirmation checkpoint to delivery package entry, saving command output or logs as evidence.
Constraints: do not add cloud accounts, team collaboration, paid services, production deployment, complex desktop packaging, or unrelated features; do not require users to edit OpenFOAM dictionaries directly; preserve future CLI and Web architecture options.
Boundaries: write only under cfd-openfoam-agent/ and directly related files, tests, and fixtures under specs/cfd-openfoam-agent/; do not modify unrelated directories, private user files, system OpenFOAM installations, or Docker configuration.
Iteration policy: build the smallest loop for task workspace, state model, input registration, confirmation checkpoint, and delivery entry first; rerun relevant checks after each stage; inspect logs and state files before changing strategy; make at most 3 focused improvement rounds before reporting remaining risks.
Stop when: the local task shell can create a task, register inputs, pause for confirmation, record status, expose a delivery package entry, pass relevant tests or explicitly report missing environment, and record artifact paths plus runtime evidence.
Pause if: external accounts, production data, paid APIs, destructive file operations, private user material, system-level install changes, or a user decision about the exact UI technology stack is required.
```
