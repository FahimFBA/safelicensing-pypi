import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HeroCodeBlock(): ReactNode {
  return (
    <div className={styles.heroCodeWrap}>
      <div className={styles.heroCodeBar}>
        <span className={clsx(styles.dot, styles.dotRed)} />
        <span className={clsx(styles.dot, styles.dotYellow)} />
        <span className={clsx(styles.dot, styles.dotGreen)} />
        <span className={styles.heroCodeFilename}>quickstart.py</span>
      </div>
      <pre className={styles.heroCodePre}>
        <span className={styles.cmt}># install from PyPI</span>
        {'\n'}
        <span className={styles.prompt}>$ </span>
        <span className={styles.cmd}>pip install safelicensing</span>
        {'\n\n'}
        <span className={styles.kw}>import</span>
        {' '}
        <span className={styles.var}>safelicensing</span>
        {' '}
        <span className={styles.kw}>as</span>
        {' '}
        <span className={styles.var}>sl</span>
        {'\n'}
        <span className={styles.kw}>from</span>
        {' PIL '}
        <span className={styles.kw}>import</span>
        {' Image'}
        {'\n\n'}
        <span className={styles.var}>model</span>
        {' = '}
        <span className={styles.fn}>sl.load_model</span>
        {'()   '}
        <span className={styles.cmt}># bundled 6 MB model</span>
        {'\n'}
        <span className={styles.var}>image</span>
        {' = Image.'}
        <span className={styles.fn}>open</span>
        {'('}
        <span className={styles.str}>"car.jpg"</span>
        {')'}
        {'\n\n'}
        <span className={styles.var}>result</span>
        {' = '}
        <span className={styles.fn}>sl.protect_image</span>
        {'(image, seed='}
        <span className={styles.num}>0.42</span>
        {', model=model)'}
        {'\n'}
        <span className={styles.var}>result</span>
        {'.encrypted.'}
        <span className={styles.fn}>save</span>
        {'('}
        <span className={styles.str}>"protected.jpg"</span>
        {')'}
      </pre>
    </div>
  );
}

function HomepageHero(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className={clsx('container', styles.heroContent)}>
        <div className={styles.heroBadges}>
          <span className={styles.heroBadge}>v1.0.2</span>
          <span className={styles.heroBadge}>Apache-2.0</span>
          <span className={styles.heroBadge}>Python 3.8+</span>
          <span className={styles.heroBadge}>IEEE ECCE 2024</span>
        </div>
        <Heading as="h1" className={styles.heroTitle}>
          {siteConfig.title}
        </Heading>
        <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
        <div className={styles.heroButtons}>
          <Link
            className="button button--primary button--lg"
            to="/docs/intro">
            Get Started
          </Link>
          <Link
            className="button button--secondary button--lg button--outline"
            href="https://github.com/FahimFBA/safelicensing-pypi">
            GitHub
          </Link>
        </div>
        <HeroCodeBlock />
      </div>
    </header>
  );
}

const STATS = [
  {number: '6 MB',      label: 'Bundled Model'},
  {number: 'YOLOv8',    label: 'Detection'},
  {number: 'Dual-Pass', label: 'Encryption'},
  {number: 'Apache-2.0', label: 'License'},
];

function StatsStrip(): ReactNode {
  return (
    <div className={styles.statsStrip}>
      <div className="container">
        <div className="row">
          {STATS.map((s, i) => (
            <div key={i} className={clsx('col col--3', styles.statItem)}>
              <span className={styles.statNumber}>{s.number}</span>
              <span className={styles.statLabel}>{s.label}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  {
    icon: '🎯',
    title: 'One-Call API',
    desc: 'protect_image() and protect_video() handle detection and encryption end-to-end in a single function call.',
  },
  {
    icon: '🤖',
    title: 'Bundled YOLOv8 Model',
    desc: '6 MB best.pt weights ship with the package — no separate download needed, works offline immediately.',
  },
  {
    icon: '🔐',
    title: 'Chaotic Encryption',
    desc: 'Dual-pass XOR scheme using the logistic map at r=3.9. Deterministic, auditable, and seed-reproducible.',
  },
  {
    icon: '🎬',
    title: 'Video Support',
    desc: 'Frame-by-frame license plate detection and encryption with original audio preservation via MoviePy.',
  },
  {
    icon: '🖥️',
    title: 'Streamlit UI',
    desc: 'Launch a full browser interface with a single command. Upload, tune the seed, and download results.',
  },
  {
    icon: '🔬',
    title: 'Research API',
    desc: 'Low-level building blocks exposed for research: logistic_map, generate_key, shuffle_pixels, and more.',
  },
];

function FeaturesSection(): ReactNode {
  return (
    <section className={styles.featuresSection}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            Everything you need
          </Heading>
          <p className={styles.sectionSubtitle}>
            From quick one-liners to deep research-grade control
          </p>
        </div>
        <div className="row">
          {FEATURES.map((f, i) => (
            <div key={i} className="col col--4" style={{marginBottom: '1.5rem'}}>
              <div className={styles.featureCard}>
                <span className={styles.featureIcon}>{f.icon}</span>
                <h3 className={styles.featureTitle}>{f.title}</h3>
                <p className={styles.featureDesc}>{f.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function InstallSection(): ReactNode {
  return (
    <section className={styles.installSection}>
      <div className="container">
        <Heading as="h2" className={styles.installTitle}>
          Start in 30 seconds
        </Heading>
        <p className={styles.installSubtitle}>
          Install from PyPI and protect your first image
        </p>
        <div className={styles.installCmd}>
          <span className={styles.installCmdDollar}>$</span>
          <span>pip install safelicensing</span>
        </div>
        <div className={styles.installButtons}>
          <Link className="button button--primary" to="/docs/installation">
            Installation Guide
          </Link>
          <Link className="button button--secondary" to="/docs/quickstart">
            Quick Start
          </Link>
          <Link
            className="button button--outline button--secondary"
            href="https://pypi.org/project/safelicensing/">
            View on PyPI
          </Link>
        </div>
      </div>
    </section>
  );
}

function ResearchSection(): ReactNode {
  return (
    <section className={styles.researchSection}>
      <div className="container">
        <a
          className={styles.paperCard}
          href="https://ieeexplore.ieee.org/abstract/document/10534375/"
          target="_blank"
          rel="noopener noreferrer">
          <span className={styles.paperIcon}>📄</span>
          <div className={styles.paperInfo}>
            <div className={styles.paperVenue}>IEEE ECCE 2024 — Research Paper</div>
            <div className={styles.paperTitle}>
              Vehicle Number Plate Detection and Encryption in Digital Images
              Using YOLOv8 and Chaotic-Based Encryption Scheme
            </div>
            <div className={styles.paperAuthors}>
              Md. Fahim Bin Amin &amp; Israt Jahan Khan
            </div>
          </div>
          <span className={styles.paperArrow}>→</span>
        </a>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  return (
    <Layout
      title="License plate detection and encryption"
      description="SafeLicensing — YOLOv8 license plate detection and chaotic-map encryption for images and videos. One-call API, bundled model, Streamlit UI.">
      <HomepageHero />
      <main>
        <StatsStrip />
        <FeaturesSection />
        <InstallSection />
        <ResearchSection />
      </main>
    </Layout>
  );
}
