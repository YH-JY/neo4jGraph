import { useState } from 'react';

export type LayoutType = 'cose' | 'concentric' | 'breadthfirst';

export const useGraphLayout = () => {
  const [layout, setLayout] = useState<LayoutType>('cose');
  const layoutConfig = {
    name: layout,
    fit: true,
    animate: true,
    padding: 20,
  };

  return {
    layout,
    setLayout,
    layoutConfig,
  };
};
