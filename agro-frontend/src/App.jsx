import { useState } from 'react';
import './App.css';
import SearchPanel from './components/SearchPanel';
import ResultsDashboard from './components/ResultsDashboard';
import YieldCalculator from './components/YieldCalculator';
import YieldDashboard from './components/YieldDashboard';
import DiseaseAnalyzer from './components/DiseaseAnalyzer';
import DiagnosisDashboard from './components/DiagnosisDashboard';
import LoadingScreen from './components/LoadingScreen';

function App() {
  const [activeTab, setActiveTab] = useState('basic'); // 'basic', 'yield', 'disease'
  const [loading, setLoading] = useState(false);
  const [predictionData, setPredictionData] = useState(null);
  const [error, setError] = useState(null);

  const handlePredict = async (params, endpoint = '/api/predict') => {
    setLoading(true);
    setError(null);
    setPredictionData(null); // Clear previous
    try {
      const response = await fetch(`http://localhost:3001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch prediction from ${endpoint}`);
      }

      const data = await response.json();
      setPredictionData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setPredictionData(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="system-title">
          An <span className="highlight">LLM-Based</span> Agricultural Decision-Support System
        </h1>
        <p className="system-subtitle">
          Integrating Environmental Monitoring, Disease Diagnosis, and Economic Forecasting
        </p>
        <div className="author-badge">
          <span className="badge-prefix">Developed by</span>
          <span className="author-name">Vaibhav Shingade</span>
        </div>
        
        <div className="tabs-container">
          <button 
            className={`tab-btn ${activeTab === 'basic' ? 'active' : ''}`}
            onClick={() => handleTabChange('basic')}
          >
            🌱 Basic Care
          </button>
          <button 
            className={`tab-btn ${activeTab === 'yield' ? 'active' : ''}`}
            onClick={() => handleTabChange('yield')}
          >
            🚜 Yield Calculator
          </button>
          <button 
            className={`tab-btn ${activeTab === 'disease' ? 'active' : ''}`}
            onClick={() => handleTabChange('disease')}
          >
            🧪 Disease Analyzer
          </button>
        </div>
      </header>
      
      <main className="app-main">
        <div className="search-section">
           {activeTab === 'basic' && <SearchPanel onPredict={(params) => handlePredict(params, '/api/predict')} disabled={loading} />}
           {activeTab === 'yield' && <YieldCalculator onPredict={(params) => handlePredict(params, '/api/yield')} disabled={loading} />}
           {activeTab === 'disease' && <DiseaseAnalyzer onPredict={(params) => handlePredict(params, '/api/diagnose')} disabled={loading} />}
        </div>
        
        <div className="results-section">
           {loading && <LoadingScreen />}
           {error && <div className="error-message glass-panel">{error}</div>}
           
           {!loading && !error && predictionData && (
             <>
               {activeTab === 'basic' && <ResultsDashboard data={predictionData} />}
               {activeTab === 'yield' && <YieldDashboard data={predictionData} />}
               {activeTab === 'disease' && <DiagnosisDashboard data={predictionData} />}
             </>
           )}

           {!loading && !error && !predictionData && (
             <div className="empty-state glass-panel">
                <div className="empty-icon">
                  {activeTab === 'basic' && '🌿'}
                  {activeTab === 'yield' && '🌾'}
                  {activeTab === 'disease' && '🔬'}
                </div>
                <h3>Ready to Analyze</h3>
                <p>
                  {activeTab === 'basic' && 'Enter a plant name and environmental conditions to get AI-powered care instructions.'}
                  {activeTab === 'yield' && 'Enter your farm size and crop type to estimate commercial yields and profits.'}
                  {activeTab === 'disease' && 'Describe your plant\'s symptoms to receive an AI diagnosis and treatment plan.'}
                </p>
             </div>
           )}
        </div>
      </main>
    </div>
  );
}

export default App;
