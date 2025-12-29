import { useEffect } from 'react';
import { useGraphStore } from '../state/useStore';

const Sidebar = () => {
  const { loadPresets, presetQueries, executeQuery, importCluster, loading, nodes, edges } = useGraphStore();

  useEffect(() => {
    loadPresets();
  }, [loadPresets]);

  const insightCards = [
    { label: '图谱节点', value: nodes.length },
    { label: '图谱关系', value: edges.length },
    { label: '预置策略', value: presetQueries.length },
  ];

  return (
    <aside className="sidebar surface-card">
      <div className="sidebar-card highlight">
        <div className="section-title">
          <span>运行概览</span>
          <small>实时刷新</small>
        </div>
        <div className="kpi-grid">
          {insightCards.map((insight) => (
            <div key={insight.label} className="kpi-card">
              <span>{insight.label}</span>
              <strong>{insight.value ?? 0}</strong>
            </div>
          ))}
        </div>
        <p className="status-note">最近一次导入成功，数据保持一致性。</p>
      </div>

      <section className="sidebar-section">
        <div className="section-title">
          <span>数据操作</span>
          <small>敏捷导入 · 一键复盘</small>
        </div>
        <button className="btn btn-primary" onClick={() => importCluster()} disabled={loading}>
          {loading ? '导入中...' : '导入集群'}
        </button>
        <button className="btn btn-soft" onClick={() => importCluster(true)} disabled={loading}>
          {loading ? '准备示例...' : '载入示例数据'}
        </button>
      </section>

      <section className="sidebar-section">
        <div className="section-title">
          <span>预置洞察</span>
          <small>一键定位高风险</small>
        </div>
        <div className="preset-list">
          {presetQueries.map((preset) => (
            <button key={preset.id} className="preset-button" onClick={() => executeQuery(preset.query)}>
              <div className="preset-label">{preset.label}</div>
              <div className="preset-desc">{preset.description}</div>
            </button>
          ))}
        </div>
      </section>

      <div className="sidebar-card neutral">
        <h4>领导关注</h4>
        <p>视图强调关键节点、跨集群路径与高风险链路，适合周会与专项汇报展示。</p>
      </div>
    </aside>
  );
};

export default Sidebar;
