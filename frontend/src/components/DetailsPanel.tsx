import { useGraphStore, UiGraphNode, UiGraphEdge } from '../state/useStore';

const DetailsPanel = () => {
  const { selected } = useGraphStore();

  if (!selected) {
    return (
      <aside className="details-panel surface-card">
        <div className="details-empty">
          <h3>态势详情</h3>
          <p>选择任意节点或关系，即可查看属性与上下文，辅助决策复盘。</p>
        </div>
      </aside>
    );
  }

  const entries = Object.entries(selected.data.properties);
  const isNode = selected.type === 'node';
  const identifier = isNode
    ? (selected.data as UiGraphNode).key
    : `${(selected.data as UiGraphEdge).source} → ${(selected.data as UiGraphEdge).target}`;

  return (
    <aside className="details-panel surface-card">
      <div className="section-title">
        <span>{selected.type === 'node' ? '节点详情' : '关系详情'}</span>
        <small>属性实时回传</small>
      </div>
      <div className="details-card">
        <div className="details-meta">唯一标识：{identifier}</div>
        {entries.length === 0 ? (
          <p className="status-note">暂无额外属性。</p>
        ) : (
          <table className="details-table">
            <tbody>
              {entries.map(([key, value]) => (
                <tr key={key}>
                  <td>{key}</td>
                  <td>{typeof value === 'object' ? JSON.stringify(value) : String(value)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </aside>
  );
};

export default DetailsPanel;
