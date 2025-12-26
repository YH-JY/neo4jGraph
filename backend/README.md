# Backend Service

FastAPI 实现的后端，涵盖配置管理、K8s 数据采集、Neo4j 图谱写入、Cypher 查询代理、攻击路径分析、导入导出与认证。

## 运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

若需指定配置文件，修改 `.env` 中的 `APP_CONFIG_FILE` 或设置环境变量。

## 测试

```bash
pytest
```

## 主要模块

- `app/core/settings.py` — 负责加载/合并 YAML 与环境变量配置。
- `app/services/neo4j_service.py` — Neo4j 驱动连接、查询与写入封装。
- `app/kube/collector.py` — 调用 Kubernetes API 拉取资源。
- `app/attack/rules.py` — RBAC、容器逃逸等攻击模式识别。
- `app/services/graph_builder.py` — DTO 转换成节点/关系并写入 Neo4j。
- `app/api/routes/*.py` — REST API。

更多细节请阅读源码内注释。
