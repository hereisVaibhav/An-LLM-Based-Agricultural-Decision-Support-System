import { useState, useMemo } from 'react';
import './YieldCalculator.css';

// Hardcoded region data for research reproducibility — no external API dependency
const REGION_DATA = {
  'India': {
    flag: '🇮🇳',
    currency: 'INR (₹)',
    regions: [
      'Maharashtra', 'Punjab', 'Uttar Pradesh', 'Madhya Pradesh', 'Karnataka',
      'Rajasthan', 'Tamil Nadu', 'Andhra Pradesh', 'Telangana', 'Gujarat',
      'Haryana', 'West Bengal', 'Bihar', 'Odisha', 'Assam',
      'Kerala', 'Chhattisgarh', 'Jharkhand', 'Himachal Pradesh', 'Uttarakhand'
    ]
  },
  'USA': {
    flag: '🇺🇸',
    currency: 'USD ($)',
    regions: [
      'Iowa', 'California', 'Texas', 'Illinois', 'Kansas',
      'Nebraska', 'Minnesota', 'Indiana', 'North Dakota', 'Ohio',
      'Wisconsin', 'South Dakota', 'Missouri', 'Michigan', 'Georgia',
      'Arkansas', 'Washington', 'Florida', 'Oregon', 'Colorado'
    ]
  },
  'China': {
    flag: '🇨🇳',
    currency: 'CNY (¥)',
    regions: [
      'Heilongjiang', 'Henan', 'Shandong', 'Sichuan', 'Hunan',
      'Jiangsu', 'Anhui', 'Hebei', 'Jiangxi', 'Hubei',
      'Guangdong', 'Yunnan', 'Guangxi', 'Inner Mongolia', 'Jilin'
    ]
  },
  'Brazil': {
    flag: '🇧🇷',
    currency: 'BRL (R$)',
    regions: [
      'Mato Grosso', 'Paraná', 'Rio Grande do Sul', 'Goiás', 'Minas Gerais',
      'São Paulo', 'Mato Grosso do Sul', 'Bahia', 'Santa Catarina', 'Tocantins'
    ]
  },
  'Australia': {
    flag: '🇦🇺',
    currency: 'AUD (A$)',
    regions: [
      'New South Wales', 'Western Australia', 'Queensland', 'Victoria',
      'South Australia', 'Tasmania', 'Northern Territory'
    ]
  },
  'Nigeria': {
    flag: '🇳🇬',
    currency: 'NGN (₦)',
    regions: [
      'Kano', 'Kaduna', 'Benue', 'Niger', 'Oyo',
      'Kebbi', 'Zamfara', 'Taraba', 'Nassarawa', 'Plateau'
    ]
  },
  'Indonesia': {
    flag: '🇮🇩',
    currency: 'IDR (Rp)',
    regions: [
      'Java', 'Sumatra', 'Kalimantan', 'Sulawesi', 'Papua',
      'Bali', 'Nusa Tenggara', 'Maluku'
    ]
  },
  'Pakistan': {
    flag: '🇵🇰',
    currency: 'PKR (₨)',
    regions: [
      'Punjab', 'Sindh', 'Khyber Pakhtunkhwa', 'Balochistan',
      'Gilgit-Baltistan', 'Islamabad Capital Territory'
    ]
  },
  'Argentina': {
    flag: '🇦🇷',
    currency: 'ARS ($)',
    regions: [
      'Buenos Aires', 'Córdoba', 'Santa Fe', 'Entre Ríos',
      'Tucumán', 'Salta', 'Santiago del Estero', 'Mendoza'
    ]
  },
  'Thailand': {
    flag: '🇹🇭',
    currency: 'THB (฿)',
    regions: [
      'Central Thailand', 'Northeastern Thailand', 'Northern Thailand',
      'Southern Thailand', 'Eastern Thailand'
    ]
  }
};

const COUNTRIES = Object.keys(REGION_DATA);

const YieldCalculator = ({ onPredict, disabled }) => {
  const [plant, setPlant] = useState('');
  const [farmSizeAcres, setFarmSizeAcres] = useState('');
  const [temperature, setTemperature] = useState('');
  const [country, setCountry] = useState('India');
  const [region, setRegion] = useState('');

  const regions = useMemo(() => {
    return REGION_DATA[country]?.regions || [];
  }, [country]);

  const selectedFlag = REGION_DATA[country]?.flag || '🌍';
  const selectedCurrency = REGION_DATA[country]?.currency || '';

  const handleCountryChange = (e) => {
    setCountry(e.target.value);
    setRegion(''); // Reset region when country changes
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!plant || !farmSizeAcres) return;
    
    onPredict({
      plant,
      farmSizeAcres: Number(farmSizeAcres),
      temperature: Number(temperature),
      country,
      region: region || undefined
    });
  };

  return (
    <div className="search-panel glass-panel">
      <h2>Commercial Yield</h2>
      <p className="subtitle">Estimate your harvest timeline and potential profit.</p>
      
      <form onSubmit={handleSubmit} className="search-form">
        <div className="form-group">
          <label htmlFor="yield-plant">Crop Type</label>
          <input 
            type="text" 
            id="yield-plant" 
            value={plant}
            onChange={(e) => setPlant(e.target.value)}
            placeholder="e.g., Wheat, Corn, Soybeans"
            required
            disabled={disabled}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="yield-country">{selectedFlag} Country</label>
            <select 
              id="yield-country" 
              value={country}
              onChange={handleCountryChange}
              disabled={disabled}
              className="form-select"
            >
              {COUNTRIES.map((c) => (
                <option key={c} value={c}>
                  {REGION_DATA[c].flag} {c}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="yield-region">State / Region</label>
            <select 
              id="yield-region" 
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              disabled={disabled}
              className="form-select"
            >
              <option value="">— National Average —</option>
              {regions.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
        </div>

        {selectedCurrency && (
          <div className="currency-hint">
            Prices will be shown in <strong>{selectedCurrency}</strong>
          </div>
        )}

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="farm-size">Farm Size (Acres)</label>
            <input 
              type="number" 
              id="farm-size" 
              value={farmSizeAcres}
              onChange={(e) => setFarmSizeAcres(e.target.value)}
              placeholder="e.g., 50"
              required
              disabled={disabled}
              min="0.1"
              step="0.1"
            />
          </div>

          <div className="form-group">
            <label htmlFor="yield-temp">Average Temp (°C)</label>
            <input 
              type="number" 
              id="yield-temp" 
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder="e.g., 25"
              disabled={disabled}
            />
          </div>
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={disabled || !plant || !farmSizeAcres}
        >
          {disabled ? 'Calculating...' : 'Calculate Yield'}
        </button>
      </form>
    </div>
  );
};

export default YieldCalculator;
