# 云原生攻击路径图谱平台

端到端平台：从 Kubernetes 集群抽取安全数据、建模攻击路径写入 Neo4j，再以 Web UI 图形化展示节点与关系。参考 Wiz 风格，支持 RBAC 权限风险与容器逃逸等攻击模式识别。

## 功能概览

- **数据采集**：基于 kubeconfig 读取 Pod/Node/ServiceAccount/Role/Binding/Secret/ConfigMap/Service/Ingress 等资源。
- **攻击建模**：自动检测高权限 RBAC 绑定、特权容器/hostPath 等逃逸场景，并生成 `AttackTechnique` 节点与 `POSSIBLE_ATTACK_PATH` 边。
- **Neo4j 写入**：统一节点/关系建模（RUNS_ON、USES_SERVICEACCOUNT、CONTAINS、BOUND_TO、CAN_ACCESS 等），通过 Bolt 批量写入并附带索引脚本。
- **API 能力**：配置管理、集群导入、Cypher 执行、节点/边详情、预置查询、图谱导出（PNG/SVG/JSON/Cypher）、认证与速率限制。
- **前端可视化**：React + Cytoscape.js 绘制多布局图谱，侧边栏提供导入、预置查询与过滤，右侧详情面板展示属性，底部 Console 输入 Cypher。
- **部署支持**：提供 Dockerfile、docker-compose、一键初始化脚本与示例 kubeconfig。

## 目录结构

```
backend/   FastAPI 服务（K8s 采集、Neo4j、攻击规则、API、测试）
frontend/  React + Vite + Cytoscape 前端
config/    配置样例与示例 kubeconfig
scripts/   Neo4j 初始化脚本
docs/      需求文档与说明
```

## 快速启动

1. **准备配置**
   ```bash
   cp backend/.env.example backend/.env
   cp config/application.yaml.example config/application.yaml
   # 根据实际环境修改 Neo4j/kubeconfig/API/安全策略
   ```
2. **启动 Neo4j**（本地或自建）：`docker compose up neo4j -d`，初次执行会加载 `scripts/init_neo4j.cypher` 创建索引。
3. **后端运行**
   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```
4. **前端运行**
   ```bash
   cd frontend
   npm install
   npm run dev -- --host
   ```
5. 浏览器访问 `http://localhost:5173`，通过侧边认证面板登录（默认 `admin/admin123`），导入集群或示例数据，运行 Cypher 并交互查看图谱。

## Docker Compose（可选）

```bash
docker compose up --build
```

- `backend` 容器会挂载 `./config` 读取 `application.yaml`。
- `frontend` 容器通过 nginx 服务构建产物，默认暴露 `4173`。
- Neo4j 账号密码默认为 `neo4j/neo4j`，可在 compose 中修改。

## 常用 API（部分）

- `POST /api/auth/token` — 使用默认管理员凭据获取 JWT。
- `POST /api/import/k8s?mock=true` — 导入集群或示例数据。
- `POST /api/cypher` — 执行任意 Cypher，自动施加行数/耗时限制并返回图谱结构。
- `GET /api/preset-queries` — 预置查询列表。
- `POST /api/export` — 导出 PNG/SVG/JSON/Cypher（PNG/SVG 基于 NetworkX+Matplotlib 快速快照）。

更多端点详见 `backend/app/api/routes`。

## 测试

后端包含单元与集成示例（配置加载、攻击检测、图构建、API）。运行：

```bash
cd backend
python -m pytest
```

> 当前执行环境未预装 Python，可在具备 Python 3.11 的机器上运行上述命令。

## 关键文件

- `config/application.yaml.example` — 平台/Neo4j/Kubernetes/同步/安全配置样例，可被环境变量覆盖。
- `scripts/init_neo4j.cypher` — 创建 Pod/Node/ServiceAccount/Role/Binding/AttackTechnique 等索引与约束。
- `backend/app/attack/rules.py` — RBAC 权限提升与容器逃逸检测逻辑。
- `backend/app/services/graph_builder.py` — 将 Kubernetes 资源与攻击节点转换为 Neo4j MERGE 语句。
- `frontend/src/components/GraphCanvas.tsx` — Cytoscape 渲染与布局切换。

## 常见问题

- **连接 Neo4j 失败**：确认 `config/application.yaml` 中的 `neo4j.uri` 与凭据正确，且 Bolt 端口 7687 可达。
- **kubeconfig 权限不足**：建议使用只读账号，至少具备 `list/get` Pod/Role/Binding/Secret 等权限。
- **Cypher 超时/行数限制**：可在配置中调整 `platform.max_cypher_rows` 与 `platform.max_cypher_time_ms`。
- **导出图谱模糊**：PNG/SVG 由服务器端 NetworkX 渲染，可在前端使用浏览器自带导出获得更高分辨率。

更多细节请参阅 `docs/REQ-云原生攻击路径平台.md`。
