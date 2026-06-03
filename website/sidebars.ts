import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: '📖 Introduction',
    },
    {
      type: 'doc',
      id: 'installation',
      label: '📦 Installation',
    },
    {
      type: 'doc',
      id: 'quickstart',
      label: '🚀 Quick Start',
    },
    {
      type: 'doc',
      id: 'cli',
      label: '🖥️ CLI Usage',
    },
    {
      type: 'category',
      label: 'API Reference',
      collapsible: false,
      collapsed: false,
      items: [
        {type: 'doc', id: 'api/protect-image', label: 'protect_image()'},
        {type: 'doc', id: 'api/protect-video', label: 'protect_video()'},
        {type: 'doc', id: 'api/load-model', label: 'load_model()'},
        {type: 'doc', id: 'api/low-level', label: 'Low-level API'},
      ],
    },
    {
      type: 'doc',
      id: 'encryption-details',
      label: '🔐 Encryption Details',
    },
    {
      type: 'doc',
      id: 'development',
      label: '🛠️ Development',
    },
    {
      type: 'doc',
      id: 'citation',
      label: '📚 Citation',
    },
  ],
};

export default sidebars;
