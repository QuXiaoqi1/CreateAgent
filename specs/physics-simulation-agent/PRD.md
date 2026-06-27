# Physics Simulation Agent PRD

版本：v0.1
状态：平台化需求草案
来源：由 `specs/cfd-openfoam-agent/PRD.md` 升级而来
阶段：第 1 步，物理模拟 Agent 平台 PRD

## 1. 产品定位

Physics Simulation Agent 是一个面向非专业模拟用户的生产级物理模拟 Agent 平台。用户通过自然语言、截图、数据表格和已有文件描述一个具体物理模拟问题，系统自动完成问题澄清、物理域识别、求解器选择、输入文件生成、运行环境检查、模拟执行、失败诊断、结果后处理和分析报告交付。

一句话目标：

把一个具体物理模拟问题自动推进到可运行、可复现、可解释的模拟交付包。

## 2. 平台策略

本产品不做一开始覆盖所有物理领域的“万能模拟器”。第一版采用“通用平台底座 + 领域包”的策略：

- 通用平台底座：任务管理、输入理解、Physics Problem Schema、solver registry、执行编排、日志诊断、报告交付、测试体系。
- MVP 领域包：CFD/OpenFOAM。
- 后续领域包：热传导、结构力学、自定义 PDE、多体动力学、多物理场。
- 第一产品表面：GitHub CLI extension，本地命令名建议为 `gh physics-sim`。

## 3. MVP 边界

MVP 仍然以 CFD/OpenFOAM 为第一领域包，覆盖：

- 二维直管流动。
- 二维弯管流动。
- 房间通风。
- 绕流问题。
- 本机 OpenFOAM 优先，Docker/OpenFOAM 镜像兜底。
- 根据明确数据做简化几何重建；数据不明显或歧义时追问用户。
- 输出语言根据用户输入决定，第一版默认中文加英文。
- 通过 GitHub CLI extension 形式提供第一版本地入口。

MVP 不实现：

- 全物理领域自动求解。
- 复杂 CAD 自动修复。
- 燃烧、化学反应、复杂多相流、强耦合多物理场。
- 云端队列、HPC 集群、企业权限系统。
- 正式工程认证或替代专家审查。
- 依赖 GitHub 远程仓库或 GitHub 登录才能完成本地模拟。

## 3.1 GitHub CLI Extension 产品形态

MVP 建议作为 GitHub CLI extension 发布，扩展仓库名建议为：

```text
gh-physics-sim
```

用户命令形态：

```bash
gh physics-sim init
gh physics-sim new "simulate airflow through a 2D bend pipe"
gh physics-sim add-table ./params.xlsx
gh physics-sim draft
gh physics-sim validate
gh physics-sim generate
gh physics-sim run
gh physics-sim status
gh physics-sim report
gh physics-sim package
gh physics-sim doctor
```

产品原则：

- `gh` extension 是本地产品入口，不要求用户必须把模拟项目托管到 GitHub。
- 如果用户在 Git 仓库中运行，系统可以把任务工作区放在项目内可配置目录。
- 如果用户不在 Git 仓库中运行，系统仍应支持本地任务目录。
- GitHub 相关能力第一版只做可选增强，例如读取仓库上下文、生成 issue/PR 摘要，不作为 MVP 必需。
- 扩展应遵守 GitHub CLI extension 的命名和安装习惯，支持本地开发安装和后续 GitHub 仓库安装。

## 4. 目标用户

### 4.1 核心用户

- 没有 CFD、有限元、多体动力学等专业模拟经验，但需要完成工程或科研模拟的人。
- 能描述物理现象和输入条件，但不知道如何选择模型、求解器、网格、边界条件和后处理方式的人。
- 需要得到可运行交付包，而不只是理论建议的人。

### 4.2 次级用户

- 会基础工程计算，但不熟悉 OpenFOAM、FEniCSx、MOOSE、Chrono 等工具的人。
- 想快速验证概念方案的工程师或研究人员。
- 需要将模拟流程标准化、批量化、可复现的团队。

## 5. 用户问题

- 不知道自己的问题属于 CFD、热传导、结构、PDE、多体动力学还是多物理场。
- 不知道需要哪些输入参数、单位、边界条件和材料属性。
- 不知道如何把截图、表格、文字说明变成求解器输入文件。
- 不会安装、检测或选择本机求解环境。
- 运行失败后无法理解求解器日志。
- 得到结果后无法判断收敛性、守恒性、可信度和适用范围。
- 难以形成可复现、可交付、可复查的模拟报告。

## 6. 产品目标

### 6.1 业务目标

- 降低开源物理模拟工具的使用门槛。
- 将模拟工作从“专家手工配置”推进到“Agent 引导生成、验证、交付”。
- 建立可持续扩展的 solver adapter 和 domain pack 生态。

### 6.2 产品目标

- 自动识别用户问题所属物理领域。
- 自动抽取并校验几何、材料、边界、初始条件和目标指标。
- 缺失信息时进行最小必要追问。
- 根据领域包能力选择求解器和模拟策略。
- 生成可运行求解器输入。
- 检查本机或容器运行环境。
- 执行模拟、捕获日志、诊断失败。
- 输出完整交付包和非专家可读报告。

## 7. 核心概念

### 7.1 Physics Problem Schema

平台统一使用 Physics Problem Schema 表示模拟问题。它是从用户输入到求解器文件生成之间的核心契约。

核心字段：

- `simulationObjective`：模拟目标、用户关注指标。
- `physicsDomain`：物理域，例如 CFD、heat-transfer、solid-mechanics、pde、multibody、multiphysics。
- `governingModel`：控制方程、简化假设、稳态/瞬态。
- `geometry`：几何类型、尺寸、拓扑、坐标系、来源证据。
- `materials`：流体、固体或其他介质属性。
- `initialConditions`：初始场或初始状态。
- `boundaryConditions`：入口、出口、壁面、载荷、约束、热边界等。
- `meshStrategy`：网格生成方式、维度、质量要求。
- `timeStrategy`：稳态、瞬态、时间步、结束条件。
- `solverStrategy`：求解器、数值方法、收敛准则。
- `postprocessingTargets`：要输出的物理量、图表和指标。
- `assumptions`：默认值、假设、风险、用户确认状态。
- `provenance`：每个关键值来自用户输入、截图、表格、默认值还是推断。
- `validation`：阻塞错误、警告、可默认项、超范围判断。

### 7.2 Domain Pack

Domain Pack 是一个物理领域能力包，包含：

- 支持的问题类型。
- schema 子类型和校验规则。
- 默认模型和求解策略。
- solver adapter。
- 模板和输入文件生成器。
- 黄金案例和测试 fixture。
- 领域报告指标。
- 超范围拒绝策略。

MVP Domain Pack：

- `domain-pack-cfd-openfoam`

后续候选：

- `domain-pack-heat-transfer`
- `domain-pack-solid-mechanics`
- `domain-pack-pde-fenicsx`
- `domain-pack-multibody-chrono`
- `domain-pack-multiphysics-moose`

### 7.3 Solver Adapter

Solver Adapter 是平台调用具体求解器的边界层，负责：

- 将通用 schema 转成求解器输入。
- 生成运行脚本。
- 检查运行环境。
- 执行命令或容器。
- 解析日志和结果。
- 暴露 solver 能力边界。

MVP 必须实现：

- `OpenFOAMAdapter`

后续候选：

- `FenicsxAdapter`
- `MooseAdapter`
- `ChronoAdapter`

## 8. 输入范围

### 8.1 自然语言

用户可以用日常语言描述问题，例如：

- “我想模拟空气流过二维弯管，入口速度 5 m/s，出口常压。”
- “帮我看这个房间通风有没有死角。”
- “这是一块板，两侧温度不同，帮我算稳态温度分布。”
- “我想模拟一个弹簧质量系统的振动。”

### 8.2 截图

截图可包含：

- 几何示意图。
- 工况说明。
- 边界条件标注。
- 表格截图。
- 论文、标准或产品资料中的局部参数。

规则：

- 明确数据可以用于构建简化几何或参数。
- 模糊数据必须追问。
- 截图提取值必须保存来源和确认状态。

### 8.3 数据表格

支持：

- CSV。
- XLSX。
- 粘贴表格文本。
- 后续可扩展 JSON/YAML。

表格可包含：

- 几何尺寸。
- 材料和流体属性。
- 工况参数。
- 边界条件。
- 参数扫描条件。

## 9. 输出交付包

一次成功任务输出完整交付包：

- `README.md`：问题摘要、运行方式、目录说明。
- `problem.schema.json`：确认后的 Physics Problem Schema。
- `assumptions.md`：假设、默认值、用户确认记录。
- `solver-input/`：具体求解器输入文件，例如 OpenFOAM case。
- `run.sh` 或等效执行入口。
- `logs/`：环境检查、网格、求解、后处理日志。
- `results/`：关键结果数据、图表、采样文件。
- `report.md`：非专家可读分析报告。
- `metadata.json`：平台版本、domain pack、solver adapter、求解器版本、运行环境。
- 可选 `report.pdf` 和压缩包。

失败任务也应输出：

- 失败阶段。
- 原始日志。
- 结构化诊断。
- 建议修复步骤。
- 是否需要用户补充信息或专家介入。

## 10. 产品流程

1. 用户创建模拟任务并输入自然语言、截图或表格。
2. 系统识别物理领域和候选 domain pack。
3. 系统抽取 Physics Problem Schema 草案。
4. 系统检查缺失参数、单位、边界条件、几何歧义和超范围风险。
5. 用户补充或确认关键信息。
6. 系统选择 solver adapter 和求解策略。
7. 系统生成求解器输入文件。
8. 系统检查本机或容器运行环境。
9. 系统执行模拟并记录日志。
10. 系统解析结果和失败信息。
11. 系统输出交付包和报告。

## 11. MVP 功能需求

### 11.1 平台底座

- 本地优先任务工作区。
- 任务状态和 artifact registry。
- 用户确认 checkpoint。
- 可被未来 CLI/Web 复用的 workflow controller。
- GitHub CLI extension 作为第一版用户入口。

### 11.1.1 GitHub CLI Extension

- 提供 `gh physics-sim` 命令组。
- 支持初始化任务工作区。
- 支持创建模拟任务和登记输入文件。
- 支持 schema draft、validate、generate、run、status、report、package、doctor。
- 支持本地安装验证：`gh extension install .`。
- 支持不登录 GitHub 的本地核心工作流。
- 支持后续可选 GitHub 集成：issue 摘要、PR 附件说明、release artifact。

### 11.2 领域识别和输入理解

- 支持自然语言、截图提取结果、CSV/XLSX、粘贴表格。
- 识别问题是否属于 MVP 支持的 CFD/OpenFOAM。
- 对非 CFD 或超出 MVP 的问题进入“暂不自动求解，但可生成问题草案”的路径。

### 11.3 Physics Problem Schema

- 定义通用 schema。
- 为 CFD/OpenFOAM 定义领域扩展。
- 支持 provenance、assumption、validation。
- 阻止未确认、缺单位、低置信度值进入求解。

### 11.4 Solver Registry

- 注册 domain pack 和 solver adapter。
- 查询 solver 能力边界。
- 根据 schema 选择适配器。
- 对超范围请求给出人类可理解解释。

### 11.5 CFD/OpenFOAM Domain Pack

- 支持二维直管、二维弯管、房间通风、绕流。
- 支持 `blockMesh` 生成简化几何。
- 支持 `simpleFoam`、`icoFoam`、`pisoFoam` 或 `pimpleFoam` 的 MVP 路线。
- 生成 OpenFOAM case、运行脚本和 metadata。

### 11.6 执行引擎

- 本机 OpenFOAM 优先。
- Docker/OpenFOAM 兜底。
- 命令日志捕获。
- `checkMesh` 解析。
- solver 日志解析。
- 失败诊断和可恢复阶段。

### 11.7 验证、报告和交付

- 输出中英默认报告。
- 明确说明假设、限制、收敛、守恒或基础 sanity check。
- 区分“可运行”和“可信”。
- 支持完整交付包导出。

## 12. 后续领域路线

### 12.1 热传导

- 一维/二维稳态热传导。
- 简单瞬态热扩散。
- 可通过 OpenFOAM、FEniCSx 或专用轻量求解器实现。

### 12.2 结构力学

- 悬臂梁变形。
- 薄板受压。
- 简单线弹性静力问题。

### 12.3 自定义 PDE

- Poisson 方程。
- 扩散方程。
- 波动方程。
- 候选求解器：FEniCSx。

### 12.4 多体动力学

- 摆。
- 弹簧质量系统。
- 简化车辆或刚体运动。
- 候选求解器：Project Chrono。

### 12.5 多物理场

- 热-结构。
- 流固耦合的简化问题。
- 候选框架：MOOSE、OpenFOAM coupling、Chrono FSI 等。

## 13. EARS 验收标准

### 13.1 平台输入

- When the user submits a physical simulation request, the system shall identify the likely physics domain and supported domain pack status.
- When the input includes tables, the system shall parse values, units, and provenance into the Physics Problem Schema draft.
- When the input includes screenshots, the system shall require confirmation before using extracted values in solver input generation.
- When the user runs `gh physics-sim new`, the system shall create or select a local simulation task workspace without requiring GitHub authentication.

### 13.2 Schema 和边界

- When required physical parameters are missing, the system shall pause and ask targeted clarification questions.
- When a value is defaulted, the system shall record the default, rationale, risk, and approval state.
- When the request exceeds supported domain pack capability, the system shall refuse automatic solving and recommend human review or a future domain pack.

### 13.3 Solver 选择和输入生成

- When a confirmed CFD/OpenFOAM schema matches a supported MVP case, the system shall select OpenFOAMAdapter and generate a runnable OpenFOAM case.
- When a problem belongs to a non-MVP physics domain, the system shall create a structured problem draft but not claim solver execution support.
- When solver input is generated, the system shall include metadata showing domain pack, solver adapter, solver version target, and selection rationale.

### 13.4 执行和诊断

- When local OpenFOAM is compatible, the system shall use local execution and record the detected version.
- When local OpenFOAM is unavailable and Docker is available, the system shall run through the configured Docker/OpenFOAM image.
- When a solver command fails, the system shall capture the command, exit code, relevant log excerpt, probable cause, and recommended next action.

### 13.5 报告和交付

- When simulation completes, the system shall generate a delivery package containing schema, assumptions, solver input, logs, results, metadata, and report.
- When generating the report, the system shall distinguish runnable status, convergence status, sanity checks, limitations, and confidence.
- When the user downloads the package, the system shall include enough information to reproduce the run in a compatible environment.

### 13.6 GitHub CLI Extension

- When the extension is installed locally with `gh extension install .`, the user shall be able to run `gh physics-sim --help`.
- When the user runs `gh physics-sim doctor`, the extension shall report gh version, workspace status, OpenFOAM availability, Docker availability, and writable task directory status.
- When the user runs the MVP command sequence, the extension shall complete a local mocked workflow without requiring GitHub login.
- When the user is inside a Git repository, the extension shall not modify tracked files unless the user explicitly chooses a workspace path inside the repo.

## 14. 生产级要求

- 稳定性：每个阶段都有状态、日志和失败原因。
- 执行准确性：solver 输入必须能追溯到 schema 和用户确认。
- 可扩展性：新领域通过 domain pack 和 solver adapter 接入。
- 部署成功：第一版通过 GitHub CLI extension 本地可运行，后续保留 Web/桌面架构。
- 测试覆盖：schema、输入解析、adapter registry、OpenFOAM case 生成、执行、日志解析、报告交付。
- 用户体验：非专家不需要直接编辑求解器输入文件。
- 可复现性：交付包包含 schema、假设、命令、版本、日志、结果和报告。

## 15. 参考工具和官方文档锚点

这些不是 MVP 全部实现范围，但用于后续 adapter 设计调研：

- OpenFOAM standard solvers: `https://doc.cfd.direct/openfoam/user-guide-v13/standard-solvers`
- GitHub CLI extensions: `https://docs.github.com/en/github-cli/github-cli/creating-github-cli-extensions`
- GitHub CLI extension create manual: `https://cli.github.com/manual/gh_extension_create`
- DOLFINx/FEniCSx Python docs: `https://docs.fenicsproject.org/dolfinx/main/python/`
- MOOSE Framework docs: `https://mooseframework.inl.gov/`
- Project Chrono docs: `https://api.projectchrono.org/`

## 16. Plan 拆分

- `plans/01-platform-product-shell/plan.md`
- `plans/02-physics-problem-schema/plan.md`
- `plans/03-domain-intake-clarification/plan.md`
- `plans/04-solver-registry-adapters/plan.md`
- `plans/05-cfd-openfoam-domain-pack/plan.md`
- `plans/06-execution-environment-engine/plan.md`
- `plans/07-validation-report-delivery/plan.md`
- `plans/08-testing-production-readiness/plan.md`
- `plans/09-github-cli-extension/plan.md`

## 17. 剩余产品问题

- 已确认：第一版本地产品入口采用 GitHub CLI extension，建议仓库名 `gh-physics-sim`，命令名 `gh physics-sim`。
- 剩余问题：extension 实现语言使用 Go、Node.js 还是 Python。默认建议 Go，便于做预编译 gh extension。
- 报告是否需要企业或学校固定模板。
- 是否需要在 MVP 后优先做热传导还是结构力学领域包。
- Docker/OpenFOAM 默认镜像版本需要在实现时确定。
