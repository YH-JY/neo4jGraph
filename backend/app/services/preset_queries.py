from __future__ import annotations

from typing import List

from app.schemas.api import PresetQuery


PRESET_QUERIES: List[PresetQuery] = [
    PresetQuery(
        id="all",
        label="全部节点",
        query="MATCH (n) RETURN n",
        description="列出图中所有节点",
    ),
    PresetQuery(
        id="sa-permissions",
        label="ServiceAccount 权限",
        query="MATCH (sa:ServiceAccount)-[r:CAN_ACCESS]->(role) RETURN sa, r, role",
        description="查看 ServiceAccount 与其角色绑定",
    ),
    PresetQuery(
        id="container-escape",
        label="容器逃逸路径",
        query="MATCH (p:Pod)-[:POSSIBLE_ATTACK_PATH]->(a:AttackTechnique {technique:'Container_Escape'}) RETURN p,a",
        description="定位潜在容器逃逸风险",
    ),
]
