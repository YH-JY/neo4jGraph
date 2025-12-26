import { useGraphStore } from '../state/useStore';

const CypherConsole = () => {
  const { query, setQuery, executeQuery, loading, error } = useGraphStore();

  return (
    <div className="cypher-console">
      <textarea
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        style={{ width: '100%', height: 80, background: '#0f172a', color: '#e2e8f0', border: '1px solid #1e293b', borderRadius: 8 }}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <button onClick={() => executeQuery()} disabled={loading} style={{ ...buttonStyle, opacity: loading ? 0.6 : 1 }}>
          执行查询
        </button>
        {error && <span style={{ color: '#f97316' }}>{error}</span>}
      </div>
    </div>
  );
};

const buttonStyle: React.CSSProperties = {
  background: '#22c55e',
  border: 'none',
  color: '#0f172a',
  padding: '6px 12px',
  borderRadius: 6,
  cursor: 'pointer',
};

export default CypherConsole;
