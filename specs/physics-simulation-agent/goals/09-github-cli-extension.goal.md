# Goal 09: GitHub CLI Extension

## 推荐执行版（中文，可直接复制）

```text
/goal 基于 specs/physics-simulation-agent/PRD.md 和 specs/physics-simulation-agent/plans/09-github-cli-extension/plan.md，把 Physics Simulation Agent 做成第一版 GitHub CLI extension `gh-physics-sim`，让用户能通过 `gh physics-sim` 在本地执行 doctor、init、new、add-file/add-table、draft、validate、generate、run、status、report 和 package 命令的 MVP 工作流。
验证：先读取 PRD、对应 plan、GitHub CLI extension 官方文档和项目已有命令；创建或更新 `gh-physics-sim` 扩展结构；运行最小测试；本地验证 `gh extension install .`、`gh physics-sim --help`、`gh physics-sim doctor`；用 mock 平台模块走通 init -> new -> status 的本地流程，并保存命令输出作为证据。
约束：不要求 GitHub 登录才能使用本地核心流程；不发布远程 release、不创建 GitHub issue/PR、不接入付费服务、不强制安装 OpenFOAM/Docker；不把 GitHub 远程集成作为 MVP 必需；不要重复实现平台模拟逻辑，CLI 只做产品入口和编排。
边界：只写入 `gh-physics-sim/` 或当前实现目录中与 GitHub CLI extension、命令路由、workspace、安全检查、测试和文档直接相关的文件，以及 specs/physics-simulation-agent/ 中必要说明；不要修改系统 gh 配置、用户全局 Git 配置、OpenFOAM/Docker 系统配置或无关项目文件。
迭代策略：先实现可安装扩展和 `--help`，再实现 `doctor`，然后实现 `init/new/status` mock 闭环，最后接入 draft/validate/generate/run/report/package 的占位或平台调用；每完成一组命令就运行测试和本地 gh 验证；同一错误连续失败 2 次后读取 gh extension 文档和命令日志再调整。
完成条件：`gh physics-sim --help` 和 `gh physics-sim doctor` 可通过本地安装运行，`init -> new -> status` mock 流程可用，命令不会要求 GitHub 登录，测试通过或明确说明缺失 gh 环境，README 写明安装、命令和限制，验证输出已记录。
暂停条件：需要发布到远程 GitHub 仓库、创建 release、使用 GitHub token、修改系统级 gh/Git 配置、安装大型依赖、决定实现语言变更、访问生产数据或执行破坏性操作时暂停。
```

## 默认选择理由

先做 GitHub CLI extension 的本地 mock 闭环，可以最快让产品有可安装、可运行的入口，同时不把开发阻塞在真实 solver 和 GitHub 远程集成上。

## Goal Draft (English-compatible)

```text
/goal Package Physics Simulation Agent as the first GitHub CLI extension `gh-physics-sim` from specs/physics-simulation-agent/PRD.md and specs/physics-simulation-agent/plans/09-github-cli-extension/plan.md, exposing an MVP local workflow through `gh physics-sim` commands for doctor, init, new, add-file/add-table, draft, validate, generate, run, status, report, and package.
Verification: inspect the PRD, matching plan, official GitHub CLI extension documentation, and existing project commands first; create or update the `gh-physics-sim` extension structure; run the smallest tests; locally verify `gh extension install .`, `gh physics-sim --help`, and `gh physics-sim doctor`; complete an init -> new -> status local flow with mocked platform modules and save command output as evidence.
Constraints: do not require GitHub login for the local core workflow; do not publish remote releases, create GitHub issues/PRs, integrate paid services, or force-install OpenFOAM/Docker; do not make GitHub remote integration an MVP requirement; do not duplicate platform simulation logic, since the CLI should remain a product entry point and orchestrator.
Boundaries: write only files directly related to the GitHub CLI extension, command routing, workspace safety, tests, and docs under `gh-physics-sim/` or the current implementation directory, plus necessary notes under specs/physics-simulation-agent/; do not modify system gh configuration, global Git configuration, system OpenFOAM/Docker configuration, or unrelated project files.
Iteration policy: implement the installable extension and `--help` first, then `doctor`, then the `init/new/status` mocked loop, and finally placeholders or platform calls for draft/validate/generate/run/report/package; run tests and local gh verification after each command group; after 2 repeated failures, inspect gh extension docs and command logs before changing strategy.
Stop when: `gh physics-sim --help` and `gh physics-sim doctor` run through local installation, the `init -> new -> status` mocked flow works, commands do not require GitHub login, tests pass or missing gh environment is explicitly reported, README documents installation, commands, and limits, and verification output is recorded.
Pause if: publishing to a remote GitHub repository, creating releases, using a GitHub token, modifying system-level gh/Git configuration, installing large dependencies, changing implementation language, accessing production data, or destructive operations are required.
```
