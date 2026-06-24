import { useState } from 'react'
import axios from 'axios'

const PATTERNS = [
  'Flower Kolam',
  'Star Kolam',
  'Pulli Kolam',
  'Lotus Kolam',
  'Sikku Kolam',
  'Rangoli Kolam',
]

export default function GenerateSection() {
  const [pattern, setPattern] = useState('Flower Kolam')
  const [color, setColor] = useState('#FF6B35')
  const [size, setSize] = useState(3)
  const [image, setImage] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function generate() {
    const safeSize = Math.min(6, Math.max(1, Number(size) || 3))
    setSize(safeSize)
    setLoading(true)
    setError('')
    try {
      const { data } = await axios.post('/api/generate', { pattern, color, size: safeSize })
      setImage(data.image)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Generation failed. Start the backend and try again.')
    } finally {
      setLoading(false)
    }
  }

  function download() {
    if (!image) return
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${image}`
    link.download = `${pattern.replace(/\s+/g, '_')}.png`
    link.click()
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="card-title">Generate Custom Kolam</div>

        <div className="generate-form">
          <div className="form-group">
            <label className="form-label" htmlFor="pattern">Pattern Type</label>
            <select id="pattern" className="form-select" value={pattern} onChange={(e) => setPattern(e.target.value)}>
              {PATTERNS.map((p) => <option key={p}>{p}</option>)}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="colour">Colour</label>
            <input id="colour" type="color" className="form-input" value={color} onChange={(e) => setColor(e.target.value)} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="size">Size (1-6)</label>
            <input
              id="size"
              type="number"
              className="form-input"
              min={1}
              max={6}
              value={size}
              onChange={(e) => setSize(e.target.value)}
            />
          </div>

          <button className="btn btn-gold" onClick={generate} disabled={loading} type="button">
            {loading ? 'Generating...' : 'Generate'}
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}
      </div>

      {loading && (
        <div className="loading-box">
          <div className="spinner" />
          <span>Generating {pattern}...</span>
        </div>
      )}

      {image && !loading && (
        <div className="card">
          <div className="card-title">{pattern}</div>
          <img src={`data:image/png;base64,${image}`} alt={pattern} className="preview-img" />
          <div className="action-row">
            <button className="btn btn-secondary" onClick={download} type="button">
              Download PNG
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
