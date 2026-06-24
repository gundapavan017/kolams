export default function KolamResult({ result }) {
  if (!result) {
    return (
      <div className="card">
        <div className="card-title">Recreation and Variations</div>
        <div className="empty-state">
          <p>After analysis, the recreated kolam and generated variations will appear here.</p>
        </div>
      </div>
    )
  }

  function download(b64, name) {
    const link = document.createElement('a')
    link.href = `data:image/png;base64,${b64}`
    link.download = name
    link.click()
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="card-title">Recreated Kolam</div>
        <img src={`data:image/png;base64,${result.recreated}`} alt="Recreated Kolam" className="preview-img" />
        <div className="action-row">
          <button className="btn btn-secondary" onClick={() => download(result.recreated, 'kolam_recreated.png')} type="button">
            Download
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-title">Generated Variations</div>
        <div className="result-grid">
          {result.variations.map((v, i) => (
            <div className="result-item" key={v.slice(0, 24)}>
              <img src={`data:image/png;base64,${v}`} alt={`Variation ${i + 1}`} />
              <div className="result-item-label">
                <span>Variation {i + 1}</span>
                <button className="mini-btn" onClick={() => download(v, `kolam_variation_${i + 1}.png`)} type="button">
                  Download
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
