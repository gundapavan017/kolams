import { useEffect, useRef, useState } from 'react'
import axios from 'axios'

export default function UploadSection({ onResult }) {
  const fileRef = useRef(null)
  const selectedFile = useRef(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [drag, setDrag] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

  function handleFile(file) {
    if (!file || !file.type.startsWith('image/')) {
      setError('Please upload an image file such as JPG, PNG, or WEBP.')
      return
    }
    if (preview) URL.revokeObjectURL(preview)
    selectedFile.current = file
    setError('')
    setPreview(URL.createObjectURL(file))
    onResult(null)
  }

  function onDrop(e) {
    e.preventDefault()
    setDrag(false)
    handleFile(e.dataTransfer.files[0])
  }

  function clearFile() {
    if (preview) URL.revokeObjectURL(preview)
    selectedFile.current = null
    if (fileRef.current) fileRef.current.value = ''
    setPreview(null)
    setError('')
    onResult(null)
  }

  async function analyze() {
    if (!selectedFile.current) return
    setLoading(true)
    setError('')
    const form = new FormData()
    form.append('file', selectedFile.current)
    try {
      const { data } = await axios.post('/api/analyze', form)
      onResult(data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Analysis failed. Start the backend and try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card">
      <div className="card-title">Upload Kolam Image</div>

      <div
        className={`upload-zone ${drag ? 'drag-over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
        onDragLeave={() => setDrag(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') fileRef.current?.click()
        }}
      >
        <input
          ref={fileRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => handleFile(e.target.files[0])}
        />
        {preview ? (
          <img src={preview} alt="Selected kolam preview" className="preview-img upload-preview" />
        ) : (
          <div className="upload-text">
            <strong>Drag and drop a kolam image here</strong>
            or click to browse your files
            <span>Supports JPG, PNG, and WEBP</span>
          </div>
        )}
      </div>

      {error && <div className="error-box">{error}</div>}

      <div className="action-row">
        <button className="btn btn-primary" onClick={analyze} disabled={!preview || loading} type="button">
          {loading ? 'Analyzing...' : 'Analyze Kolam'}
        </button>
        {preview && (
          <button className="btn btn-secondary" onClick={clearFile} type="button">
            Clear
          </button>
        )}
      </div>

      {loading && (
        <div className="loading-box">
          <div className="spinner" />
          <span>Detecting dots, symmetry, and loops...</span>
        </div>
      )}
    </div>
  )
}
