# 云原生攻击路径平台需求文档

## 一、背景

目标：开发一个 Web 平台，用于展示云原生（Kubernetes 环境）攻击路径图谱，支持从真实 k8s 集群获取数据、导入 Neo4j 图数据库，并通过前端以图形化方式交互展示攻击路径与节点关系，便于安全分析与关联查询。
参考实现（样式与攻击路径建模）：Wiz、KubeHound。

## 二、总体功能概述

- 从用户提供的 kubeconfig 获取本地 k8s 集群真实数据（对象与关系）。
- 提取并标准化 Kubernetes 资源实体、权限关系与攻击技术（至少包含 RBAC 权限风险、容器逃逸 等手段）。
- 将资源与攻击路径建模为图谱，并通过 bolt 协议写入 Neo4j（Neo4j 在本地通过 Docker 运行，地址可配置）。
- Web 平台提供后端服务（数据抽取、转换、Neo4j 交互、API）和前端应用（图谱渲染、查询、交互、导入导出）。
- 支持通过输入 Cypher 语句查询并渲染结果（例如：执行 Cypher：MATCH(n)RETURNn 时展现全部节点与边并将存在关系的节点用线连起来）。
- 图谱渲染风格参考 Wiz，要求美观、清晰、交互友好（节点/边样式、聚合、过滤、侧边详情面板等）。

## 三、功能性需求（详细）

### 数据采集与建图

- 从 kubeconfig 指定的集群读取资源：Pod、Container（可视为 Pod 下容器）、Node、ServiceAccount、Role、RoleBinding、ClusterRole、ClusterRoleBinding、ConfigMap、Secret、Volume、PersistentVolume、Ingress、Service、Credential（外部凭证/密钥）等。
- 解析 RBAC 关联：Role/ClusterRole -> Permission、RoleBinding/ClusterRoleBinding -> Subject（ServiceAccount/User/Group）。
- 自动识别并建模攻击手段/路径模式（至少实现 RBAC 权限风险、容器逃逸），并将这些“攻击手段”作为图谱上的关系或中间节点，使路径可追溯。
- 支持将采集到的数据转换为 Neo4j 节点与关系（Node/Edge），并通过 Bolt 协议写入。

### Neo4j 连接与配置

- Neo4j 的连接地址（示例初始值：192.168.40.129）、Bolt 端口、用户名、密码等通过项目配置文件配置，可运行时修改并支持多环境。
- 提供初始化脚本（如 Cypher 脚本或后端接口）用于创建必要索引、约束与基础数据模型。

### 查询与渲染

- 支持用户通过 UI 输入任意 Cypher 语句并执行，返回结果可视化渲染（节点与边），例如执行全量查询：MATCH(n)RETURNn 应展示所有节点与它们存在的关系边（若只返回节点，则通过查询补全关系以便渲染成连通图，或提示用户执行关系查询）。
- 提供常用预置查询按钮（如“查找与某 ServiceAccount 相关的所有权限与 Pod”、“查找可能的容器逃逸路径”等）。
- 渲染时将节点按照类型区分样式（颜色/图标/形状），边按照关系类型区分（线型/箭头/颜色），并在鼠标悬停或点击时显示侧边详情（节点属性、相关资源、来源对象等）。
- 支持节点/边筛选、搜索、聚焦（聚焦后高亮相关子图）、缩放与布局切换（力导向、层次布局等）。
- 支持导出图谱快照（PNG/SVG）与导出 Cypher/JSON。

### 前后端代码

- 前端需实现完整 UI（图谱渲染、查询面板、配置面板、结果详情、登录/认证如果需要）、状态管理与与后端 API 的通讯。
- 后端需实现 API（kube 数据采集、Neo4j 写入/读出、Cypher 执行代理、配置管理、后台任务管理）、安全控制与日志。
- 前后端均为项目的一部分，必须提供源码与构建脚本。

### 配置项（必须可通过配置文件修改）

- Neo4j: 地址、bolt 端口、用户名、密码、数据库名（如适用）。
- Kubernetes: kubeconfig 文件路径或内容、读取超时/证书校验开关。
- 平台: 后端监听地址与端口、前端构建配置、日志级别、最大返回节点/边数限制等。
- 其他：是否允许外部网络访问 Neo4j、是否执行自动定时同步、同步周期等。

### 安全与权限

- 后端执行 Cypher 要有执行限制（防止超大查询导致 OOM）；对高风险语句采用白名单/超时/返回行限制等保护。
- kubeconfig 的使用需谨慎：支持仅读权限的 kubeconfig，建议在文档中注明权限要求。
- 支持基本认证或令牌机制保护后端 API（如果平台面向多人使用）。

## 四、非功能需求

- 响应时间：图谱渲染（中小规模图，1000 节点内）初次渲染目标 < 3s（网络与机器资源允许情况下）。
- 可扩展性：后端设计支持添加新的攻击检测规则（插件化或策略配置）。
- 可配置性：所有敏感或环境特异配置均通过配置文件或环境变量管理。
- 可维护性：代码需有清晰 README、注释与模块划分，测试覆盖关键逻辑（至少单元测试与集成测试）。
- 兼容性：前端在主流浏览器（Chrome、Edge、Firefox 最新版本）可正常使用。
- 可视化美观度：节点样式与布局应参考 Wiz（直观的图标、颜色区分、交互细节）。

## 五、数据模型（建议）

### 节点类型（label）

- Container（属性：name、image、containerId、pod、namespace 等）
- Pod（name、namespace、labels、uid、node、phase）
- Node（name、os、k8sVersion、labels）
- ServiceAccount（name、namespace、uid）
- Role / ClusterRole（name、rules）
- RoleBinding / ClusterRoleBinding（name、subjects、roleRef）
- Secret（name、namespace、type、dataSummary）
- ConfigMap（name、namespace）
- Volume / PV / PVC（name、mountPath、type）
- Service（name、namespace、selector、ports）
- Ingress（name、namespace、rules）
- Credential（外部凭证，name、type、source）
- Master（控节点，name、ip 等）
- AttackTechnique（如：RBAC_Escalation、Container_Escape、Privilege_Escalation 等，带 severity、description、evidence）

### 关系类型（edge types）

- RUNS_ON (Pod -> Node)
- CONTAINS (Pod -> Container)
- MOUNTS (Pod/Container -> Volume)
- USES_SERVICEACCOUNT (Pod -> ServiceAccount)
- BOUND_TO (RoleBinding -> Subject)
- GRANTS (Role/ClusterRole -> Permission or directly to ServiceAccount via Binding)
- HAS_SECRET (Pod/Container -> Secret)
- CAN_ACCESS (Subject -> Resource) — 表示基于权限的访问能力
- POSSIBLE_ATTACK_PATH (AttackTechnique 中间节点或直接关系，用于串联可利用链)

## 六、接口与协议

- Neo4j 交互：使用 Bolt 协议（可以使用官方驱动，如 Neo4j Java/Node/Python driver），后端需实现连接池与失败重连策略。
- Kubernetes 交互：使用 kubeconfig 提供的证书/token，通过官方 k8s client（适用于后端语言，例如 Go 的 client-go、Python 的 kubernetes-client、Node 的 @kubernetes/client-node）。
- 后端 API（示例）：
  - POST /api/configure — 更新平台配置（Neo4j、kubeconfig 路径等）
  - POST /api/import/k8s — 从 kubeconfig 抽取并导入 Neo4j（支持同步/全量/增量）
  - POST /api/cypher — 执行 Cypher 查询（请求体包含语句与结果限制）
  - GET /api/graph/node/{id} — 获取节点详情
  - GET /api/graph/edge/{id} — 获取边详情
  - GET /api/preset-queries — 返回预置查询列表
  - POST /api/export — 导出图谱（PNG/SVG/JSON/Cypher）
- 前端与后端通信使用 HTTPS（若部署在有证书环境），使用 JSON 作为数据格式。

## 七、前端设计细化

- 主页面模块：
  - 顶栏：平台名、配置按钮、用户信息（若有认证）。
  - 侧边栏：数据同步/导入、预置查询、过滤器（按类型、namespace、severity 等）。
  - 中央画布：图谱渲染区域（支持缩放、拖拽、右键菜单）。
  - 右侧详情面板：显示选中节点/边的详细属性、相关日志/证据、可能的风险说明与推荐修复建议。
  - 底部/弹窗：执行 Cypher 输入与结果反馈。
- 可视化实现建议：使用 D3.js / Cytoscape.js / vis.js / Sigma.js 等图形库。Cytoscape.js 适合复杂生物样图谱；Sigma.js 更注重大图性能；D3.js 灵活但实现成本高。
- 样式建议：参考 Wiz 的配色（深色主题与浅色主题可选）、使用直观图标（Pod、Node、Secret、ServiceAccount 等）。

## 八、后端实现建议

- 技术栈（可选参考）：
  - 语言：Node.js (Express/Koa) 或 Python (FastAPI) 或 Go (Gin)。优先考虑熟悉度与 Neo4j 驱动支持。
  - Neo4j 驱动：neo4j-driver (Node.js/Python/Java)。
  - K8s 客户端：@kubernetes/client-node（Node.js）或 kubernetes python client 或 client-go（Go）。
- 数据处理：对抽取的数据进行去重、归一化与建模后写入 Neo4j。
- 定时任务：支持定时同步（可选）。
- 错误与异常处理：写入失败重试、查询超时、并发限制。
- 日志：重要操作（导入、执行 Cypher、修改配置）记录日志并可审计。

## 九、配置文件示例（建议放在项目 config/ 下，支持环境变量覆盖）

示例字段：
```
NEO4J_URI: bolt://192.168.40.129:7687
NEO4J_USER: neo4j
NEO4J_PASSWORD: your_password
KUBECONFIG_PATH: /path/to/kubeconfig
SYNC_SCHEDULE: 0 0 * * *
API_PORT: 8080
MAX_CYPHER_ROWS: 10000
ALLOW_EXTERNAL_NEOS: false
```

## 十、部署与使用说明（详细步骤）

1. 前提条件：主机可访问 Neo4j（已通过 Docker 在本地 VM 启动），示例地址：192.168.40.129，确认 Bolt 端口 7687 可达。
2. 拥有 kubeconfig 文件（可访问目标本地 k8s 集群）。
3. 已安装 Node.js、Python/Go 运行环境，或 Docker。
4. 提供初始化脚本 `init_neo4j.cypher`，后端启动时可执行。
5. 快速部署：docker-compose + Node/React（本项目采用 FastAPI/React，可类比操作）。

## 十一、测试与验收标准

- 功能验收：成功读取 kubeconfig、写入 Neo4j、执行 Cypher 并渲染、展现攻击路径、检测 RBAC/容器逃逸等。
- 性能验收：1000 节点级别图谱渲染 < 3s。
- 文档与交付：README、部署说明、配置示例、运行脚本、接口说明、测试、示例数据等齐备。

## 十二、交付物清单

- 完整源码（frontend、backend）
- 项目根 README
- config 样例文件
- scripts/init_neo4j.cypher
- 示例 kubeconfig（或说明）
- 单元&集成测试脚本
- 部署脚本 / docker-compose.yml
- 使用手册、示例数据

## 十三、优先级与里程碑（建议）

- M1：后端架构、采集、Neo4j 写入、配置与 init 脚本。
- M2：前端基础界面、Cypher 执行、基本渲染。
- M3：攻击检测规则实现、可视化增强、详情面板。
- M4：性能优化、导出、部署、测试与文档。

## 十四、备注与建议

- 针对大规模图考虑抽样/聚合。
- 攻击检测规则可配置化。
- Cypher 能力开放需限制、审计。
