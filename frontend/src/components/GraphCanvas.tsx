import { useEffect, useRef, useState } from 'react';
import cytoscape, { Core } from 'cytoscape';
import coseBilkent from 'cytoscape-cose-bilkent';

import { useGraphLayout, LayoutType } from '../hooks/useGraphLayout';
import { useGraphStore } from '../state/useStore';

cytoscape.use(coseBilkent);

const nodeStyles: Record<string, { color: string; border: string }> = {
  Pod: { color: '#4f46e5', border: '#312e81' },
  Container: { color: '#22d3ee', border: '#0e7490' },
  Node: { color: '#a78bfa', border: '#7c3aed' },
  ServiceAccount: { color: '#34d399', border: '#059669' },
  AttackTechnique: { color: '#f87171', border: '#dc2626' },
  Binding: { color: '#fbbf24', border: '#d97706' },
  Secret: { color: '#ec4899', border: '#be185d' },
  Service: { color: '#60a5fa', border: '#2563eb' },
};

const layouts: Array<{ key: LayoutType; label: string }> = [
  { key: 'cose', label: '智能' },
  { key: 'concentric', label: '同心' },
  { key: 'breadthfirst', label: '分层' },
];

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
            'text-max-width': 120,
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
      setSelected({ type: 'node', data: event.target.data().meta });
    });
    instance.on('tap', 'edge', (event) => {
      setSelected({ type: 'edge', data: event.target.data().meta });
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
    <section className="graph-panel surface-card">
      <div className="graph-toolbar">
        <div>
          <h3>拓扑总览</h3>
          <p>多布局切换以匹配不同汇报视角</p>
        </div>
        <div className="layout-chips">
          {layouts.map((item) => (
            <button
              key={item.key}
              className={`layout-chip ${layout === item.key ? 'active' : ''}`}
              onClick={() => setLayout(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div ref={containerRef} className="graph-container" />
    </section>
  );
};

export default GraphCanvas;
