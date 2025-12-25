export default function ModelResponse({ prediction, loading }) {
  if (loading) {
    return (
      <div className="section-box">
        <h3 className="section-title">🤖 AI Model Response</h3>
        <div className="loading">Analyzing...</div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="section-box">
        <h3 className="section-title">🤖 AI Model Response</h3>
        <div className="loading">Waiting for location...</div>
      </div>
    );
  }

  const riskLevel = prediction.risk_level.toLowerCase().replace(' ', '-');
  const riskClass = `risk-${riskLevel}`;

  return (
    <div className="section-box">
      <h3 className="section-title">🤖 AI Model Response</h3>
      
      {/* Risk Indicator */}
      <div className={`risk-indicator ${riskClass}`}>
        {prediction.risk_level} RISK
      </div>

      {/* Metrics Grid */}
      <div className="model-metrics">
        {Object.entries(prediction.predictions).map(([key, value]) => (
          <div key={key} className="metric-box">
            <div className="metric-label">
              {key.replace(/_/g, ' ')}
            </div>
            <div className="metric-value">
              {(value * 100).toFixed(1)}%
            </div>
          </div>
        ))}
      </div>
      
      {prediction.data_source && (
        <div style={{ fontSize: '11px', opacity: 0.6, marginTop: '10px', textAlign: 'center' }}>
          {prediction.data_source}
        </div>
      )}
    </div>
  );
}
