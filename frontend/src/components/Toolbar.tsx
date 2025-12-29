import { useGraphStore } from '../state/useStore';
import { Api } from '../services/api';

const Toolbar = () => {
  const { executeQuery, nodes, edges } = useGraphStore();

  const handleExport = async (format: string) => {
    const blob = await Api.exportGraph(format);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `graph.${format}`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <header className="top-bar surface-card">
      <div>
        <p className="app-eyebrow">云原生攻防驾驶舱</p>
        <h1 className="app-title">云原生攻击路径平台</h1>
        <p className="app-subtitle">态势可视 · 风险闭环 · 决策共识</p>
      </div>
      <div className="top-actions">
        <div className="status-pills">
          <div className="status-pill">
            <span>在线节点</span>
            <strong>{nodes.length}</strong>
          </div>
          <div className="status-pill">
            <span>图谱关系</span>
            <strong>{edges.length}</strong>
          </div>
        </div>
        <div className="action-buttons">
          <button className="btn btn-ghost" onClick={() => executeQuery('MATCH (n) RETURN n LIMIT 500')}>
            全量节点
          </button>
          <button className="btn btn-outline" onClick={() => handleExport('png')}>
            导出 PNG
          </button>
          <button className="btn btn-primary" onClick={() => handleExport('json')}>
            导出 JSON
          </button>
        </div>
      </div>
    </header>
  );
};

export default Toolbar;
