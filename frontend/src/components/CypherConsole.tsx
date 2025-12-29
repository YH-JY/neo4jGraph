import { useGraphStore } from '../state/useStore';

const CypherConsole = () => {
  const { query, setQuery, executeQuery, loading, error } = useGraphStore();

  return (
    <section className="cypher-console surface-card">
      <div className="section-title">
        <span>即时分析</span>
        <small>支持标准 Cypher 语法</small>
      </div>
      <textarea
        className="console-input"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 200"
      />
      <div className="console-footer">
        <button className="btn btn-primary" onClick={() => executeQuery()} disabled={loading}>
          {loading ? '执行中...' : '执行查询'}
        </button>
        {error && <span className="error-text">{error}</span>}
      </div>
    </section>
  );
};

export default CypherConsole;
