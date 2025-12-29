import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';
const api = axios.create({ baseURL });

export interface GraphResponse {
  nodes: Array<{ key: string; label: string; properties: Record<string, unknown> }>;
  edges: Array<{ source: string; target: string; relation: string; properties: Record<string, unknown> }>;
  raw: any[];
}

export const Api = {
  async fetchPresetQueries() {
    const { data } = await api.get('/api/preset-queries');
    return data;
  },
  async runCypher(query: string) {
    const { data } = await api.post<GraphResponse>('/api/cypher', { query });
    return data;
  },
  async importCluster(useMock = false) {
    const { data } = await api.post('/api/import/k8s', null, { params: { mock: useMock } });
    return data;
  },
  async exportGraph(format: string, query?: string) {
    const { data } = await api.post(
      '/api/export',
      { format, cypher: query },
      { responseType: 'blob' }
    );
    return data;
  },
};

export default api;
