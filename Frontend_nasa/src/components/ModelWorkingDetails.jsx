export default function ModelWorkingDetails({ prediction, loading }) {
  if (loading || !prediction) {
    return (
      <div className="section-box">
        <h3 className="section-title">⚙️ Model Working Details</h3>
        <div className="loading">Analyzing...</div>
      </div>
    );
  }

  const avgRocAuc = prediction.confidence_score || 0.74;

  return (
    <div className="section-box">
      <h3 className="section-title">⚙️ Model Working Details</h3>
      
      <div className="model-working">
        <div className="working-step active">
          <strong>📍 Location Analysis</strong><br />
          Processing geographical data<br />
          Date: {new Date().toISOString().slice(0, 10)}
        </div>
        
        <div className="working-step">
          <strong>📊 Feature Engineering</strong><br />
          Processing <span className="feature-count">222</span> features<br />
          Including: Temporal, Lag, Rolling, Interaction features
        </div>
        
        <div className="working-step">
          <strong>🤖 Model Selection</strong><br />
          Using trained <span className="model-type">Random Forest</span> models<br />
          Trained with 39 cities
        </div>
        
        <div className="working-step">
          <strong>🎯 Prediction Engine</strong><br />
          {Object.keys(prediction.predictions).length} extreme weather targets<br />
          Data source: {prediction.data_source || 'ML Model'}
        </div>
        
        <div className="working-step">
          <strong>📈 Model Performance</strong><br />
          Average ROC-AUC: <span className="confidence-score">{(avgRocAuc * 100).toFixed(1)}%</span><br />
          Training cities: 29 Indian + 10 US states
        </div>
      </div>
    </div>
  );
}
