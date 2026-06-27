# CFD OpenFOAM Agent PRD

版本：v0.1
状态：需求已确认，计划已拆分
阶段：第 2 步完成，等待第 3 步生成 /goal 提示词

## 1. 产品定位

本产品是一个面向没有 CFD 专业知识、缺少模拟经验用户的生产级 Agent 系统。用户通过自然语言、截图、数据表格等输入描述一个具体的 CFD 模拟问题，系统自动将问题推进到 OpenFOAM 可运行求解，并输出完整交付包，包括可执行算例、运行记录、结果后处理、分析报告和复现实验说明。

一句话目标：

把一个具体的 CFD 模拟问题自动推进到 OpenFOAM 可运行求解，并交付用户能理解、能复现、能判断结果可信度的完整 CFD 分析包。

## 2. 目标用户

### 2.1 核心用户

- 没有 CFD 专业训练，但需要完成流体仿真分析的工程、产品、科研或教学用户。
- 会描述问题背景，但不会独立完成几何、网格、边界条件、求解器选择、OpenFOAM 字典配置和结果后处理的用户。
- 需要可运行结果，而不只是理论建议的用户。

### 2.2 次级用户

- 有基础工程知识但不熟悉 OpenFOAM 的用户。
- 想用 OpenFOAM 快速验证概念方案的工程师。
- 需要把仿真过程标准化、批量化、可复现的团队。

## 3. 用户问题

当前目标用户通常卡在以下环节：

- 不知道如何把真实工程问题转化为 CFD 模拟问题。
- 不知道该选择稳态、瞬态、不可压、可压、湍流、传热、多相等哪类模型。
- 不会准备 OpenFOAM case 目录和关键字典文件。
- 不会判断网格质量、边界条件、初始条件是否合理。
- 运行失败后不懂日志错误含义。
- 得到结果后不知道如何解读，无法判断结果是否可信。
- 难以把一次模拟整理成可复现、可交付的报告。

## 4. 产品目标

### 4.1 业务目标

- 将非专业用户从“只有问题描述”推进到“获得 OpenFOAM 可运行交付包”。
- 降低 OpenFOAM 使用门槛，让用户不需要先系统学习 CFD 才能完成标准模拟。
- 用流程化 Agent 将 CFD 问题定义、算例生成、运行、验证和报告输出串成闭环。

### 4.2 产品目标

- 支持自然语言、截图、表格作为问题输入。
- 自动澄清缺失参数，并给出合理默认值与风险说明。
- 自动选择 OpenFOAM 求解路径，生成可运行 case。
- 自动运行基础检查与求解流程。
- 自动解析求解日志、残差、关键物理量和失败原因。
- 自动输出完整交付包。

### 4.3 非目标

- MVP 不追求覆盖所有 CFD 物理模型。
- MVP 不替代专业 CFD 工程师对高风险工程结论的最终审查。
- MVP 不保证用户输入极度缺失时仍能给出可靠数值结论。
- MVP 不优先支持复杂 CAD 自动修复、复杂动网格、燃烧、化学反应、强耦合多物理场。

## 5. 生产级标准

本产品中的“生产级”至少包括：

- 稳定性：流程失败时能定位阶段、错误原因和恢复建议。
- 执行准确性：生成的 OpenFOAM case 与用户问题、物理模型、边界条件保持一致。
- 部署成功：Web、CLI、桌面端至少有一种可稳定部署，核心计算服务可被重复调用。
- 测试覆盖：核心 case 生成、参数校验、命令编排、日志解析、报告生成有自动化测试。
- 用户体验：用户无需理解 OpenFOAM 目录细节，也能完成输入、确认、运行、查看报告。
- 可复现性：交付包中包含输入、假设、配置、命令、版本、日志、结果和报告。

## 6. 产品形态

产品最终形态支持独立 Web、CLI、桌面产品。MVP 第一版优先本地产品体验，后续再考虑 CLI，并在架构上保留 Web 扩展空间。

- 本地产品体验：第一版优先，适合非专业用户在本机完成输入、确认、运行、查看报告和下载交付包。
- Web 架构预留：底层任务、状态、文件和报告接口按可被 Web 调用的方式设计。
- CLI：后续增强，适合开发、自动化、服务器部署和批处理。
- 桌面端：作为后续增强，封装本地 OpenFOAM 环境、文件管理和可视化体验。

MVP 不强制三端同时完整实现，但底层 Agent workflow、case 生成、运行和报告能力必须可被本地产品、未来 CLI 和未来 Web 复用。

## 6.1 运行环境策略

MVP 采用“用户本机 OpenFOAM 优先，Docker/OpenFOAM 镜像兜底”的运行策略：

- 当用户本机已有兼容 OpenFOAM 环境时，系统优先检测并使用本机 OpenFOAM。
- 当本机未检测到 OpenFOAM 或版本不兼容时，系统使用 Docker/OpenFOAM 镜像封装运行环境。
- 系统需要在交付包中记录实际使用的运行环境、OpenFOAM 版本、Docker 镜像信息和关键命令。
- 系统需要在运行前做环境检查，并给出用户可理解的修复建议。

## 7. 输入范围

### 7.1 自然语言输入

用户可以用日常语言描述问题，例如：

- “我想模拟空气流过一个二维弯管，入口速度 5 m/s，出口常压。”
- “帮我分析一个房间通风效果，看看速度分布和死角。”
- “我有一个水流过管道的压降问题，管径和流量在表格里。”

### 7.2 截图输入

截图可包含：

- 几何示意图。
- 工况说明。
- 边界条件标注。
- 表格截图。
- 参考论文或规范中的局部参数。

MVP 中截图能力以“提取文字和结构化信息”为基础。若截图或配套数据中包含明确几何尺寸、边界标注和拓扑关系，系统应尝试生成可运行的简化几何；若几何信息不明显、不完整或存在歧义，系统必须向用户追问，而不是猜测生成。

### 7.3 数据表格输入

表格可包含：

- 几何尺寸。
- 流体属性。
- 工况参数。
- 入口、出口、壁面等边界条件。
- 多组参数扫描条件。

MVP 支持 CSV、XLSX 和用户粘贴表格文本。

## 8. 输出交付包

一次成功任务应输出一个完整交付包，至少包含：

- `README.md`：问题摘要、运行方式、目录说明。
- `assumptions.md`：系统采用的假设、默认值、用户确认记录。
- `case/`：OpenFOAM 可运行算例目录。
- `run.sh` 或等效执行入口：可复现运行命令。
- `logs/`：网格生成、检查、求解、后处理日志。
- `results/`：关键结果数据、图表、采样文件。
- `report.md` 或 `report.pdf`：面向非专业用户的分析报告。
- `metadata.json`：OpenFOAM 版本、Agent 版本、模型选择、时间戳、输入摘要。

可选输出：

- ParaView 可打开的结果说明。
- 参数扫描对比表。
- 失败诊断报告。
- 可复现实验压缩包。

## 9. MVP 能力范围

### 9.1 问题理解与澄清

系统需要识别：

- 模拟目标。
- 几何类型。
- 维度：2D、2.5D、3D。
- 流体类型和物性。
- 流动状态：稳态或瞬态。
- 入口、出口、壁面、对称面等边界。
- 关注指标：速度、压力、压降、流量、涡区、温度等。
- 用户缺失参数。

系统需要在必要时发起澄清，而不是直接生成不可信 case。

### 9.2 模型与求解器选择

MVP 优先支持：

- 单相流。
- 不可压流。
- 稳态或简单瞬态。
- 2D 或简单 3D 几何。
- 常见湍流模型。
- 简单传热作为可选增强。

MVP 第一批标准案例覆盖：

- 二维直管流动。
- 二维弯管流动。
- 房间通风。
- 绕流问题。

MVP 可优先支持以下 OpenFOAM 路线：

- `blockMesh` 生成规则几何网格。
- `simpleFoam` 处理稳态不可压湍流问题。
- `pisoFoam` 或 `pimpleFoam` 处理简单瞬态不可压问题。
- `icoFoam` 处理低雷诺数层流瞬态问题。
- `checkMesh` 做网格质量检查。
- `postProcess` 做基础后处理。

### 9.3 Case 生成

系统需要生成：

- `0/` 初始和边界条件。
- `constant/` 物理属性、湍流属性、几何网格配置。
- `system/` 控制参数、离散格式、求解器设置。
- 网格脚本和运行脚本。

### 9.4 自动运行与诊断

系统需要：

- 调用 OpenFOAM 命令。
- 捕获标准输出、错误输出和退出码。
- 解析典型错误。
- 判断是否进入可运行、运行失败、结果异常、结果完成等状态。
- 在失败时输出用户能理解的修复建议。

### 9.5 后处理与报告

系统需要：

- 提取关键物理量。
- 汇总残差和收敛状态。
- 生成基础图表或数据表。
- 用非 CFD 专业用户能理解的语言解释结果。
- 明确说明结果可信度、假设限制和建议下一步。

## 10. 核心用户流程

1. 用户输入自然语言需求，并上传截图或数据表格。
2. 系统解析输入，生成结构化模拟问题草案。
3. 系统列出缺失项、风险项和建议默认值。
4. 用户确认或补充信息。
5. 系统选择求解器、物理模型和网格策略。
6. 系统生成 OpenFOAM case。
7. 系统执行网格检查和求解。
8. 系统根据运行结果自动诊断。
9. 系统生成后处理结果和分析报告。
10. 用户下载完整交付包。

## 11. 功能需求

### 11.1 需求采集

- 系统应支持自然语言输入。
- 系统应支持上传截图并提取文本信息。
- 系统应支持 CSV、XLSX、粘贴表格文本。
- 系统应将用户输入转化为结构化 CFD 问题定义。

### 11.2 参数澄清

- 系统应识别缺失的关键参数。
- 系统应区分必须澄清项和可默认项。
- 系统应展示默认值来源、适用范围和风险。
- 用户确认前，系统不得执行高风险模拟。

### 11.3 求解策略生成

- 系统应根据问题类型选择 OpenFOAM 求解器。
- 系统应说明求解器、湍流模型和网格策略的选择理由。
- 系统应在超出 MVP 能力时拒绝直接运行，并给出人工介入建议。

### 11.4 OpenFOAM Case 生成

- 系统应生成符合 OpenFOAM 目录结构的 case。
- 系统应生成可复现运行脚本。
- 系统应保存所有输入、假设和生成配置。

### 11.5 执行编排

- 系统应按阶段执行网格生成、网格检查、求解和后处理。
- 系统应记录每个阶段的命令、日志、耗时和状态。
- 系统应支持失败后从可恢复阶段重新运行。

### 11.6 结果分析

- 系统应解析残差、收敛状态和关键物理量。
- 系统应将结果转化为用户可理解的结论。
- 系统应标注结果局限性和不确定性。

### 11.7 交付包生成

- 系统应生成完整交付目录。
- 系统应支持下载压缩包。
- 系统应包含复现说明和版本信息。

## 12. EARS 验收标准

### 12.1 输入与理解

- When the user submits a natural-language CFD problem, the system shall extract the simulation objective, geometry, fluid, boundary conditions, and target outputs into a structured problem definition.
- When the user uploads a CSV or XLSX file, the system shall parse tabular parameters and attach them to the structured problem definition.
- When the user uploads a screenshot, the system shall attempt to extract visible text and ask for confirmation before using extracted values in a simulation.

### 12.2 澄清与风险控制

- When required simulation parameters are missing, the system shall pause execution and ask the user to provide or approve those parameters.
- When a parameter can be defaulted, the system shall display the default value, reason, and risk before continuing.
- When the requested problem exceeds the MVP-supported physics scope, the system shall refuse automatic execution and provide a human-review recommendation.

### 12.3 Case 生成

- When the user confirms the structured problem definition, the system shall generate an OpenFOAM case directory containing `0`, `constant`, and `system`.
- When the system generates a case, it shall include a runnable script that reproduces the mesh, solver run, and post-processing commands.
- When the system selects a solver, it shall record the solver name and selection rationale in the delivery package.

### 12.4 执行与诊断

- When the system runs `checkMesh`, it shall record the full log and summarize whether the mesh passed critical checks.
- When an OpenFOAM command fails, the system shall capture the command, exit code, relevant log excerpt, probable cause, and recommended next action.
- When the solver completes, the system shall summarize convergence status and key monitored values.

### 12.5 报告与交付

- When the simulation completes successfully, the system shall generate a delivery package containing case files, logs, results, assumptions, metadata, and an analysis report.
- When the report is generated, it shall explain the result in non-expert language and include assumptions, limitations, and recommended next steps.
- When the user downloads the package, the system shall provide all files needed to reproduce the simulation in a compatible OpenFOAM environment.

## 13. 关键质量要求

### 13.1 稳定性

- 所有长任务必须有阶段状态。
- 所有失败必须有可见错误原因。
- 系统不能静默吞掉 OpenFOAM 日志。

### 13.2 准确性

- 参数单位必须被显式识别或确认。
- 边界条件必须能追溯到用户输入、默认假设或用户确认。
- 求解器选择必须有可解释理由。

### 13.3 测试覆盖

MVP 至少覆盖：

- 结构化问题定义解析测试。
- 表格参数解析测试。
- OpenFOAM case 模板生成测试。
- 字典文件合法性测试。
- 命令编排测试。
- 日志解析测试。
- 交付包生成测试。

### 13.4 用户体验

- 用户界面不应要求用户直接编辑 OpenFOAM 字典文件。
- 用户应能看到当前进度、等待原因和下一步动作。
- 报告应优先解释结论，而不是堆叠原始 CFD 术语。

## 14. 建议 MVP 模块

1. 输入工作台
   - 自然语言输入
   - 截图上传
   - 表格上传
   - 文件与任务管理

2. CFD 问题建模 Agent
   - 输入解析
   - 参数抽取
   - 单位归一
   - 缺失项澄清
   - 风险识别

3. OpenFOAM 策略 Agent
   - 物理范围判断
   - 求解器选择
   - 模型选择
   - 网格策略选择

4. Case 生成器
   - 模板管理
   - 字典生成
   - 脚本生成
   - metadata 生成

5. 执行引擎
   - 命令编排
   - 阶段状态
   - 日志捕获
   - 失败恢复

6. 诊断与后处理 Agent
   - 残差解析
   - 网格质量摘要
   - 关键指标提取
   - 结果可信度判断

7. 报告与交付包生成器
   - Markdown 报告
   - PDF 报告，可后置
   - 结果目录整理
   - 压缩包导出

8. Web/CLI 产品壳
   - CLI 命令入口
   - 本地 Web 任务界面
   - 配置管理
   - 运行环境检查

## 15. 优先级建议

### P0，MVP 必须完成

- 自然语言输入到结构化问题定义。
- 缺失参数澄清。
- 基于明确数据的简化几何重建，信息不足时追问用户。
- 二维直管、二维弯管、房间通风、绕流四类标准案例的 OpenFOAM case 生成。
- `blockMesh`、`checkMesh`、求解器运行编排。
- 本机 OpenFOAM 环境检测与执行。
- Docker/OpenFOAM 镜像兜底执行。
- 日志捕获与基础失败诊断。
- Markdown 分析报告，输出语言根据用户输入自动决定，第一版默认中文加英文。
- 完整交付包导出。

### P1，第一轮增强

- CSV/XLSX 参数导入。
- 截图文字提取。
- 更多 OpenFOAM 求解器模板。
- 参数扫描。
- PDF 报告。
- 本地产品界面增强。
- CLI 命令入口。

### P2，后续增强

- 复杂 CAD/网格工具集成。
- ParaView 自动截图或可视化导出。
- 多相、传热、可压缩流等高级物理模型。
- 桌面端封装。
- 团队任务协作和历史项目库。

## 16. 后续流程接口

本 PRD 后续将被拆分为多个 `plan.md`，建议拆分方向：

- `plans/01-product-shell/plan.md`：CLI/Web 产品壳与任务状态。
- `plans/02-input-understanding/plan.md`：自然语言、截图、表格解析。
- `plans/03-cfd-problem-schema/plan.md`：结构化 CFD 问题定义与校验。
- `plans/04-openfoam-case-generator/plan.md`：OpenFOAM case 生成。
- `plans/05-execution-engine/plan.md`：命令编排、日志、失败恢复。
- `plans/06-postprocessing-report/plan.md`：结果解析、后处理和报告。
- `plans/07-testing-production-readiness/plan.md`：测试、部署、生产级保障。

在第 3 步中，计划使用以下 skill 来源撰写 `/goal` 提示词：

```bash
npx skills add joeseesun/qiaomu-goal-meta-skill
```

在第 5 步中，所有 `plan.md` 的执行结果、遗漏项、风险和下一轮计划将合并为 `consolidation.md`。

## 17. 已确认决策与剩余问题

- 已确认：MVP 第一批标准案例为二维管道、二维弯管、房间通风、绕流。
- 已确认：运行环境优先使用用户本机 OpenFOAM；若没有，则使用 Docker/OpenFOAM 镜像封装。
- 已确认：第一版优先本地产品体验，之后考虑 CLI，并保留 Web 架构。
- 已确认：输出语言根据用户输入语言决定，第一版默认中文加英文。
- 已确认：系统应根据明确数据做几何重建；若数据不明显或存在歧义，需要向用户追问。
- 剩余问题：交付报告是否需要符合企业或学校的固定模板？
