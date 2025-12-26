// 基础索引与约束
CREATE CONSTRAINT pod_name IF NOT EXISTS
FOR (p:Pod)
REQUIRE (p.uid) IS UNIQUE;

CREATE CONSTRAINT node_name IF NOT EXISTS
FOR (n:Node)
REQUIRE (n.name) IS UNIQUE;

CREATE CONSTRAINT sa_name IF NOT EXISTS
FOR (sa:ServiceAccount)
REQUIRE (sa.uid) IS UNIQUE;

CREATE CONSTRAINT role_name IF NOT EXISTS
FOR (r:Role)
REQUIRE (r.fqname) IS UNIQUE;

CREATE CONSTRAINT cluster_role_name IF NOT EXISTS
FOR (r:ClusterRole)
REQUIRE (r.name) IS UNIQUE;

CREATE CONSTRAINT binding_name IF NOT EXISTS
FOR (b:Binding)
REQUIRE (b.uid) IS UNIQUE;

CREATE CONSTRAINT attack_id IF NOT EXISTS
FOR (a:AttackTechnique)
REQUIRE (a.id) IS UNIQUE;

CREATE INDEX pod_namespace IF NOT EXISTS FOR (p:Pod) ON (p.namespace);
CREATE INDEX attack_severity IF NOT EXISTS FOR (a:AttackTechnique) ON (a.severity);
CREATE INDEX subject_kind IF NOT EXISTS FOR (s:Subject) ON (s.kind);
