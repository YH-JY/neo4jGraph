import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';

import { useGraphLayout } from '../hooks/useGraphLayout';
import { useGraphStore } from '../state/useStore';

cytoscape.use(coseBilkent);

const nodeStyles: Record<string, { color: string; border: string }> = {
  Pod: { color: '#3b82f6', border: '#1d4ed8' },
  Container: { color: '#22d3ee', border: '#0e7490' },
  Node: { color: '#a78bfa', border: '#7c3aed' },
  ServiceAccount: { color: '#34d399', border: '#059669' },
  AttackTechnique: { color: '#f87171', border: '#dc2626' },
  Binding: { color: '#fbbf24', border: '#d97706' },
  Secret: { color: '#ec4899', border: '#be185d' },
  Service: { color: '#60a5fa', border: '#2563eb' },
};

const GraphCanvas = () => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [cy, setCy] = useState<Core>();
  const { layoutConfig, setLayout, layout } = useGraphLayout();
  const { nodes, edges, setSelected } = useGraphStore();

  useEffect(() => {
    if (!containerRef.current) return;
    const instance = cytoscape({
      container: containerRef.current,
      wheelSensitivity: 0.2,
      elements: [],
      style: [
        {
          selector: 'node',
          style: {
            label: 'data(label)',
            'background-color': '#1f2937',
            'border-width': 2,
            'border-color': '#334155',
            color: '#e2e8f0',
            'font-size': 10,
            'text-wrap': 'wrap',
            'text-max-width': 80,
            'text-outline-width': 0,
          },
        },
        {
          selector: 'edge',
          style: {
            width: 1.5,
            'line-color': '#475569',
            'target-arrow-color': '#475569',
            'target-arrow-shape': 'triangle',
            label: 'data(label)',
            'font-size': 8,
            color: '#cbd5f5',
          },
        },
        {
          selector: 'node:selected',
          style: {
            'border-color': '#f97316',
            'border-width': 3,
          },
        },
      ],
    });
    instance.on('tap', 'node', (event) => {
      const data = event.target.data();
      setSelected({ type: 'node', data: data.meta });
    });
    instance.on('tap', 'edge', (event) => {
      const data = event.target.data();
      setSelected({ type: 'edge', data: data.meta });
    });
    setCy(instance);
    return () => {
      instance.destroy();
    };
  }, [setSelected]);

  useEffect(() => {
    if (!cy) return;
    cy.elements().remove();
    const elements = [
      ...nodes.map((n) => ({
        data: {
          id: n.key,
          label: n.properties.name ? `${n.label}: ${n.properties.name}` : n.label,
          meta: n,
        },
        classes: n.label,
      })),
      ...edges.map((e, idx) => ({
        data: {
          id: `${e.source}-${e.target}-${idx}`,
          source: e.source,
          target: e.target,
          label: e.relation,
          meta: e,
        },
      })),
    ];
    cy.add(elements);
    cy.nodes().forEach((node) => {
      const type = node.classes()[0];
      const palette = nodeStyles[type] || { color: '#475569', border: '#334155' };
      node.style({
        'background-color': palette.color,
        'border-color': palette.border,
      });
    });
    cy.layout(layoutConfig as any).run();
  }, [cy, nodes, edges, layoutConfig]);

  return (
    <div className="graph-panel">
      <div style={{ display: 'flex', gap: 8, padding: '8px 16px', borderBottom: '1px solid #1e293b' }}>
        <span>布局:</span>
        {['cose', 'concentric', 'breadthfirst'].map((name) => (
          <button
            key={name}
            onClick={() => setLayout(name as any)}
            style={{
              background: layout === name ? '#2563eb' : '#1e293b',
              border: 'none',
              color: '#e2e8f0',
              padding: '4px 10px',
              borderRadius: 6,
              cursor: 'pointer',
            }}
          >
            {name}
          </button>
        ))}
      </div>
      <div ref={containerRef} style={{ width: '100%', height: 'calc(100% - 48px)' }} />
    </div>
  );
};

export default GraphCanvas;
