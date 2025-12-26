import { create } from 'zustand';
import { Api, GraphResponse } from '../services/api';

export interface UiGraphNode {
  key: string;
  label: string;
  properties: Record<string, unknown>;
}

export interface UiGraphEdge {
  source: string;
  target: string;
  relation: string;
  properties: Record<string, unknown>;
}

interface SelectedItem {
  type: 'node' | 'edge';
  data: UiGraphNode | UiGraphEdge;
}

interface GraphStore {
  nodes: UiGraphNode[];
  edges: UiGraphEdge[];
  selected?: SelectedItem;
  query: string;
  presetQueries: Array<{ id: string; label: string; query: string; description: string }>;
  loading: boolean;
  error?: string;
  setQuery: (query: string) => void;
  executeQuery: (query?: string) => Promise<void>;
  importCluster: (mock?: boolean) => Promise<void>;
  loadPresets: () => Promise<void>;
  setSelected: (selected?: SelectedItem) => void;
  setGraph: (response: GraphResponse) => void;
}

export const useGraphStore = create<GraphStore>((set, get) => ({
  nodes: [],
  edges: [],
  presetQueries: [],
  query: 'MATCH (n)-[r]->(m) RETURN n,r,m',
  loading: false,
  setQuery: (query) => set({ query }),
  setSelected: (selected) => set({ selected }),
  setGraph: (response) => set({ nodes: response.nodes, edges: response.edges }),
  executeQuery: async (provided) => {
    const query = provided ?? get().query;
    set({ loading: true, error: undefined });
    try {
      const data = await Api.runCypher(query);
      set({ nodes: data.nodes, edges: data.edges, query, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
  importCluster: async (mock = false) => {
    set({ loading: true, error: undefined });
    try {
      await Api.importCluster(mock);
      await get().executeQuery('MATCH (n)-[r]->(m) RETURN n,r,m');
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },
  loadPresets: async () => {
    try {
      const presets = await Api.fetchPresetQueries();
      set({ presetQueries: presets });
    } catch (error) {
      set({ error: (error as Error).message });
    }
  },
}));
