import { useEffect } from 'react';
import { useGraphStore } from '../state/useStore';
import ConfigDrawer from './ConfigDrawer';

const Sidebar = () => {
  const { loadPresets, presetQueries, executeQuery, importCluster, loading } = useGraphStore();

  useEffect(() => {
    loadPresets();
  }, [loadPresets]);

  return (
    <div className="sidebar">
      <h3>数据操作</h3>
      <button onClick={() => importCluster()} disabled={loading} style={buttonStyle}>
        导入集群
      </button>
      <button onClick={() => importCluster(true)} disabled={loading} style={buttonStyle}>
        使用示例数据
      </button>
      <h3>预置查询</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {presetQueries.map((preset) => (
          <button
            key={preset.id}
            style={presetButtonStyle}
            onClick={() => executeQuery(preset.query)}
          >
            <strong>{preset.label}</strong>
            <small style={{ display: 'block', color: '#94a3b8' }}>{preset.description}</small>
          </button>
        ))}
      </div>
      <ConfigDrawer />
    </div>
  );
};

const buttonStyle: React.CSSProperties = {
  background: '#2563eb',
  border: 'none',
  color: '#fff',
  padding: '8px 12px',
  borderRadius: 8,
  cursor: 'pointer',
  marginBottom: 8,
};

const presetButtonStyle: React.CSSProperties = {
  background: '#1e293b',
  border: '1px solid #334155',
  color: '#e2e8f0',
  padding: '8px',
  textAlign: 'left',
  borderRadius: 8,
  cursor: 'pointer',
};

export default Sidebar;
