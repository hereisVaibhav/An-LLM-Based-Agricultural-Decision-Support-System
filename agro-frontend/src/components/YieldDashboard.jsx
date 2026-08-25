const YieldDashboard = ({ data }) => {
  if (!data) return null;

  const locationLabel = [
    data.location?.region,
    data.location?.country
  ].filter(Boolean).join(', ') || 'Not specified';

  const currencyDisplay = data.location?.currencySymbol
    ? `${data.location.currencySymbol} ${data.location.currency || ''}`
    : '';

  return (
    <div className="yield-dashboard animate-fade-in">
      <div className="dashboard-header glass-panel">
        <div className="header-info">
          <h2>{data.plant || 'Crop Yield Prediction'}</h2>
          <div className="header-tags">
            <span className="growth-stage">{data.farmSizeAcres ?? 'N/A'} Acres</span>
            <span className="location-badge">
              📍 {locationLabel}
            </span>
            {currencyDisplay && (
              <span className="currency-badge">
                💱 {currencyDisplay}
              </span>
            )}
          </div>
        </div>
      </div>

      <div className="disclaimer-banner glass-panel">
        <span className="disclaimer-icon">⚠️</span>
        <p className="disclaimer-text">
          Estimated values based on regional agricultural statistics and current market assumptions. Actual outcomes may vary.
        </p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card glass-panel water-card">
          <div className="card-icon">🚜</div>
          <h3>Estimated Yield</h3>
          <div className="metric-value">
            {data.yield?.estimatedTons ?? 'N/A'} <span>{data.yield?.unit ?? 'Tons'}</span>
          </div>
          {data.yield?.yieldPerAcre && (
            <p className="metric-sub">{data.yield.yieldPerAcre} per acre</p>
          )}
          <p className="metric-note">{data.yield?.note || 'No additional notes'}</p>
        </div>

        <div className="metric-card glass-panel env-card">
          <div className="card-icon">⏳</div>
          <h3>Harvest Timeline</h3>
          <div className="metric-value">
            {data.timeline?.daysToHarvest ?? 'N/A'} <span>Days</span>
          </div>
          <div className="stages-list">
            {(data.timeline?.stages || []).map((stage, idx) => (
              <span key={idx} className="stage-badge">{stage}</span>
            ))}
          </div>
        </div>
      </div>

      {/* ROI Highlight Card */}
      {data.financials?.roi && (
        <div className="roi-highlight glass-panel">
          <div className="roi-content">
            <div className="roi-icon">📈</div>
            <div className="roi-text">
              <span className="roi-label">Return on Investment (ROI)</span>
              <span className="roi-value">{data.financials.roi}</span>
            </div>
          </div>
        </div>
      )}

      <div className="financials-card glass-panel">
        <h3>💰 Financial Projections — {locationLabel}</h3>
        
        {data.financials?.pricePerUnit && (
          <div className="price-unit-banner">
            Market Rate: <strong>{data.financials.pricePerUnit}</strong>
            {data.financials.priceUnit && (
              <span className="price-unit-label"> / {data.financials.priceUnit}</span>
            )}
          </div>
        )}

        <div className="financials-grid">
          <div className="fin-stat revenue">
            <span className="label">Est. Market Value</span>
            <span className="value">{data.financials?.marketValueEstimate || 'N/A'}</span>
          </div>
          <div className="fin-stat cost">
            <span className="label">Fertilizer Cost</span>
            <span className="value cost-value">{data.financials?.fertilizerCostEstimate || 'N/A'}</span>
          </div>
          <div className="fin-stat cost">
            <span className="label">Labor Cost</span>
            <span className="value cost-value">{data.financials?.laborCostEstimate || 'N/A'}</span>
          </div>
          <div className="fin-stat cost">
            <span className="label">Total Cost</span>
            <span className="value cost-value">{data.financials?.totalCostEstimate || 'N/A'}</span>
          </div>
          <div className="fin-stat profit">
            <span className="label">Net Profit</span>
            <span className="value profit-value">{data.financials?.netProfit || 'N/A'}</span>
          </div>
          <div className="fin-stat profit">
            <span className="label">Profit Margin</span>
            <span className="value profit-value">{data.financials?.profitMargin || 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Price Source Citation */}
      {(data.financials?.priceSource || data.location?.priceSource) && (
        <div className="source-citation glass-panel">
          <div className="source-icon">📋</div>
          <div className="source-text">
            <span className="source-label">Pricing Data Source</span>
            <span className="source-value">{data.financials?.priceSource || data.location?.priceSource}</span>
          </div>
        </div>
      )}

      <div className="advice-section glass-panel">
        <div className="advice-block tips" style={{width: '100%'}}>
          <h3>💡 Agricultural Recommendations</h3>
          <ul>
            {(data.recommendations || []).map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default YieldDashboard;
