export default function AnalysisPanel({ rules }) {
  if (!rules) {
    return (
      <div className="card">
        <div className="card-title">Analysis Results</div>
        <div className="empty-state">
          <p>Upload and analyze a kolam image to see extracted design rules here.</p>
        </div>
      </div>
    )
  }

  const symmetryList = Array.isArray(rules.symmetry_type)
    ? rules.symmetry_type
    : [rules.symmetry_type]

  const principles = [
    { label: 'Pulli dot grid', desc: `${rules.grid_size} dot grid as structural anchor` },
    { label: 'Symmetry', desc: `${rules.symmetry_fold}-fold rotational symmetry` },
    { label: 'Closed loops', desc: `${rules.loop_count} closed curve(s) detected` },
    { label: 'Dot enclosure', desc: 'Dots are surrounded by the generated line work' },
    { label: 'Modular units', desc: `${rules.pattern_type} repeating base unit` },
  ]

  return (
    <div className="card">
      <div className="card-title">Extracted Design Rules</div>

      <div className="rules-grid">
        <Rule label="Pattern Type" value={rules.pattern_type} />
        <Rule label="Grid Size" value={rules.grid_size} />
        <Rule label="Dot Count" value={`${rules.dot_count} dots`} />
        <Rule label="Loop Count" value={`${rules.loop_count} loops`} />
        <Rule label="Symmetry Fold" value={`${rules.symmetry_fold}-fold`} />
        <Rule label="Stroke Type" value={rules.stroke_type} compact />
      </div>

      <div className="panel-block">
        <div className="rule-label">Symmetry Types Detected</div>
        {symmetryList.map((s) => <span key={s} className="badge">{s}</span>)}
      </div>

      <div className="panel-block principles-list">
        <div className="rule-label">Design Principles Identified</div>
        {principles.map((p) => (
          <div key={p.label} className="principle-line">
            <span>{p.label}: </span>{p.desc}
          </div>
        ))}
      </div>
    </div>
  )
}

function Rule({ label, value, compact = false }) {
  return (
    <div className="rule-item">
      <div className="rule-label">{label}</div>
      <div className={`rule-value ${compact ? 'compact' : ''}`}>{value}</div>
    </div>
  )
}
