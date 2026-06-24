import { useState } from 'react'
import UploadSection from './components/UploadSection.jsx'
import AnalysisPanel from './components/AnalysisPanel.jsx'
import KolamResult from './components/KolamResult.jsx'
import GenerateSection from './components/GenerateSection.jsx'
import GallerySection from './components/GallerySection.jsx'

const TABS = ['Analyze', 'Generate', 'Gallery']

const PRINCIPLES = [
  'Pulli dot grid',
  'Rotational symmetry',
  'Continuous loops',
  'Dot enclosure',
  'Modular construction',
]

export default function App() {
  const [tab, setTab] = useState('Analyze')
  const [result, setResult] = useState(null)

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="brand-mark">K</span>
          <div>
            Kolam Analyzer
            <div className="navbar-subtitle">Design rule detection and recreation</div>
          </div>
        </div>
        <div className="nav-tabs" role="tablist" aria-label="Kolam tools">
          {TABS.map((t) => (
            <button
              key={t}
              className={`nav-tab ${tab === t ? 'active' : ''}`}
              onClick={() => setTab(t)}
              type="button"
              role="tab"
              aria-selected={tab === t}
            >
              {t}
            </button>
          ))}
        </div>
      </nav>

      <main className="main">
        {tab === 'Analyze' && (
          <>
            <section className="hero">
              <div className="hero-title">
                Analyze and Recreate<br /><span>Kolam Designs</span>
              </div>
              <div className="hero-desc">
                Upload a kolam image to detect dot grids, symmetry, loops, and
                pattern type. The app recreates the design and generates related variations.
              </div>
              <div className="principles-row">
                {PRINCIPLES.map((p) => (
                  <span key={p} className="principle-chip">{p}</span>
                ))}
              </div>
            </section>

            <div className="analyze-layout">
              <div className="analyze-left">
                <UploadSection onResult={setResult} />
                <AnalysisPanel rules={result?.rules} />
              </div>
              <div className="analyze-right">
                <KolamResult result={result} />
              </div>
            </div>
          </>
        )}

        {tab === 'Generate' && (
          <>
            <div className="section-heading">
              <div className="section-title">Generate Custom Kolam</div>
              <div className="section-sub">
                Choose a pattern, colour, and size to generate a fresh kolam.
              </div>
            </div>
            <GenerateSection />
          </>
        )}

        {tab === 'Gallery' && <GallerySection />}
      </main>
    </div>
  )
}
