import { useGraphStore } from '../state/useStore';

const DetailsPanel = () => {
  const { selected } = useGraphStore();

  if (!selected) {
    return (
      <div className="details-panel">
        <h3>详情</h3>
        <p>选择节点或边查看属性。</p>
      </div>
    );
  }

  const entries = Object.entries(selected.data.properties);

  return (
    <div className="details-panel">
      <h3>{selected.type === 'node' ? '节点' : '关系'}详情</h3>
      <div style={{ fontSize: 14, color: '#94a3b8', marginBottom: 8 }}>ID: {'key' in selected.data ? selected.data.key : `${selected.data.source}->${selected.data.target}`}</div>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <tbody>
          {entries.map(([key, value]) => (
            <tr key={key} style={{ borderBottom: '1px solid #1e293b' }}>
              <td style={{ padding: '6px 4px', color: '#94a3b8' }}>{key}</td>
              <td style={{ padding: '6px 4px' }}>{JSON.stringify(value)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default DetailsPanel;
