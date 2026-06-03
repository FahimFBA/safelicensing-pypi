import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'SafeLicensing',
  tagline: 'License plate detection and chaotic-map encryption for images and videos',
  favicon: 'img/favicon.svg',

  url: 'https://fahimfba.github.io',
  baseUrl: '/safelicensing-pypi/',
  organizationName: 'FahimFBA',
  projectName: 'safelicensing-pypi',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/FahimFBA/safelicensing-pypi/edit/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.jpg',
    colorMode: {
      defaultMode: 'dark',
      respectPrefersColorScheme: true,
    },
    announcementBar: {
      id: 'v1_release',
      content:
        '🎉 <strong>SafeLicensing v1.0.3</strong> is live on PyPI — <a href="https://pypi.org/project/safelicensing/" target="_blank" rel="noopener noreferrer">pip install safelicensing</a>',
      backgroundColor: '#0c4a6e',
      textColor: '#e0f2fe',
      isCloseable: true,
    },
    navbar: {
      title: 'SafeLicensing',
      logo: {
        alt: 'SafeLicensing',
        src: 'img/logo.svg',
      },
      hideOnScroll: false,
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          to: '/docs/api/protect-image',
          position: 'left',
          label: 'API Reference',
        },
        {
          href: 'https://ieeexplore.ieee.org/abstract/document/10534375/',
          label: 'Paper',
          position: 'left',
        },
        {
          href: 'https://pypi.org/project/safelicensing/',
          label: 'PyPI',
          position: 'right',
        },
        {
          href: 'https://github.com/FahimFBA/safelicensing-pypi',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {label: 'Introduction', to: '/docs/intro'},
            {label: 'Installation', to: '/docs/installation'},
            {label: 'Quick Start', to: '/docs/quickstart'},
            {label: 'CLI Usage', to: '/docs/cli'},
          ],
        },
        {
          title: 'API Reference',
          items: [
            {label: 'protect_image()', to: '/docs/api/protect-image'},
            {label: 'protect_video()', to: '/docs/api/protect-video'},
            {label: 'load_model()', to: '/docs/api/load-model'},
            {label: 'Low-level API', to: '/docs/api/low-level'},
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'PyPI Package',
              href: 'https://pypi.org/project/safelicensing/',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/FahimFBA/safelicensing-pypi',
            },
            {
              label: 'IEEE Paper',
              href: 'https://ieeexplore.ieee.org/abstract/document/10534375/',
            },
            {
              label: 'Issues',
              href: 'https://github.com/FahimFBA/safelicensing-pypi/issues',
            },
          ],
        },
        {
          title: 'Authors',
          items: [
            {
              label: 'Md. Fahim Bin Amin',
              href: 'https://www.fahimbinamin.com',
            },
            {
              label: 'Israt Jahan Khan',
              href: 'https://www.isratjahankhan.com',
            },
            {label: 'Citation', to: '/docs/citation'},
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Md. Fahim Bin Amin & Israt Jahan Khan. Apache-2.0 License.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ['bash', 'python', 'toml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
