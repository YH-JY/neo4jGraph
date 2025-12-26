import { useGraphStore } from '../state/useStore';
import { Api } from '../services/api';

const Toolbar = () => {
  const { executeQuery } = useGraphStore();

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
    <div className="top-bar">
      <div>
        <strong>云原生攻击路径平台</strong>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button style={buttonStyle} onClick={() => executeQuery('MATCH (n) RETURN n')}>
          全量节点
        </button>
        <button style={buttonStyle} onClick={() => handleExport('png')}>
          导出 PNG
        </button>
        <button style={buttonStyle} onClick={() => handleExport('json')}>
          导出 JSON
        </button>
      </div>
    </div>
  );
};

const buttonStyle: React.CSSProperties = {
  background: '#1e293b',
  border: '1px solid #334155',
  color: '#e2e8f0',
  padding: '6px 12px',
  borderRadius: 8,
  cursor: 'pointer',
};

export default Toolbar;
