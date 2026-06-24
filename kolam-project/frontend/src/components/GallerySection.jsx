import { useEffect, useState } from 'react'
import axios from 'axios'

export default function GallerySection() {
  const [kolams, setKolams] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchGallery()
  }, [])

  async function fetchGallery() {
    setLoading(true)
    setError('')
    try {
      const { data } = await axios.get('/api/gallery')
      setKolams(data.kolams)
    } catch {
      setError('Could not load the gallery. Start the backend and try again.')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="loading-box">
        <div className="spinner" />
        <span>Generating gallery...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="error-box">{error}</div>
        <button className="btn btn-secondary retry-btn" onClick={fetchGallery} type="button">
          Retry
        </button>
      </div>
    )
  }

  return (
    <div>
      <div className="section-heading">
        <div className="section-title">Kolam Gallery</div>
        <div className="section-sub">Six generated kolam pattern families based on traditional design rules.</div>
      </div>

      <div className="gallery-grid">
        {Object.entries(kolams).map(([name, b64]) => (
          <div className="gallery-card" key={name}>
            <img src={`data:image/png;base64,${b64}`} alt={name} />
            <div className="gallery-card-name">{name}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
