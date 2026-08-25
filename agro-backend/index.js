const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const { GoogleGenerativeAI } = require('@google/generative-ai');

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

function extractJSON(text) {
  const codeBlockRegex = /```json\s*([\s\S]*?)\s*```/i;
  const match = text.match(codeBlockRegex);
  if (match) {
    try {
      return JSON.parse(match[1].trim());
    } catch (e) {}
  }

  const genericBlockRegex = /```\s*([\s\S]*?)\s*```/;
  const genericMatch = text.match(genericBlockRegex);
  if (genericMatch) {
    try {
      return JSON.parse(genericMatch[1].trim());
    } catch (e) {}
  }

  const candidates = [];
  let openIndex = text.indexOf('{');
  while (openIndex !== -1) {
    let closeIndex = text.lastIndexOf('}');
    while (closeIndex > openIndex) {
      const candidate = text.slice(openIndex, closeIndex + 1);
      try {
        const parsed = JSON.parse(candidate);
        candidates.push({ parsed, length: candidate.length });
        break;
      } catch (e) {}
      closeIndex = text.lastIndexOf('}', closeIndex - 1);
    }
    openIndex = text.indexOf('{', openIndex + 1);
  }

  if (candidates.length > 0) {
    candidates.sort((a, b) => b.length - a.length);
    return candidates[0].parsed;
  }

  return JSON.parse(text.trim());
}

const PREDICT_SYSTEM_PROMPT = `You are an expert agricultural AI assistant. Respond with ONLY a valid JSON object.
Schema:
{
  "plant": "string",
  "status": "Optimal" | "Stress" | "Critical",
  "statusMessage": "string",
  "waterRequirement": { "value": number, "unit": "L/day", "adjustment": "string" },
  "nutrition": {
    "nitrogen": { "value": number, "unit": "g/day" },
    "phosphorus": { "value": number, "unit": "g/day" },
    "potassium": { "value": number, "unit": "g/day" },
    "calcium": { "value": number, "unit": "g/day" }
  },
  "pH": { "min": number, "max": number, "optimal": number },
  "temperature": { "current": number, "optimalMin": number, "optimalMax": number, "unit": "°C" },
  "humidity": { "current": number, "optimalMin": number, "optimalMax": number, "unit": "%" },
  "growthStage": "string",
  "alerts": ["string"],
  "tips": ["string"],
  "funFact": "string"
}`;

const YIELD_SYSTEM_PROMPT = `You are an expert agricultural economist AI. Respond with ONLY a valid JSON object.

CRITICAL PRICING RULES:
1. All financial figures (market value, costs, profit) MUST be in the LOCAL CURRENCY of the specified country/region.
2. Use real-world, current-year market price benchmarks for that specific region. Examples:
   - India: Use INR (₹). Reference APMC mandi prices, government MSP (Minimum Support Price) rates, or state agricultural marketing board data. Differentiate between states (e.g., Pune APMC vs Delhi Azadpur mandi vs Punjab grain markets).
   - USA: Use USD ($). Reference USDA National Agricultural Statistics Service commodity prices. Differentiate between states (e.g., Iowa corn belt vs California specialty crops).
   - China: Use CNY (¥). Reference Ministry of Agriculture data.
   - Brazil: Use BRL (R$). Reference CONAB (National Supply Company) data.
   - Other countries: Use respective local currency and cite the national agricultural pricing authority.
3. If a specific state/region is given, use that region's local market rates — NOT national averages.
4. Always cite the pricing source in the "priceSource" field.

YIELD ESTIMATION RULES:
1. Use your knowledge of regional agricultural statistics, soil conditions, climate, and standard farming practices to estimate crop yield PER ACRE for the given crop and region.
2. CRITICAL: Yield per acre is an intrinsic agronomic property of the crop+region+climate combination. It does NOT change with farm size. A 3-acre wheat farm in Punjab and a 15-acre wheat farm in Punjab both produce the SAME yield per acre (approximately 2 Tons/Acre). The TOTAL yield scales linearly: estimatedTons = yieldPerAcre × farmSizeAcres.
3. First determine the correct yield per acre for the crop+region, then multiply by farmSizeAcres to get estimatedTons. Do NOT let the farm size influence your per-acre estimate.
4. Base your estimate on publicly available government agricultural data (e.g., USDA NASS, India Ministry of Agriculture, CONAB Brazil, UK DEFRA, FAO). Do NOT fabricate unrealistic yields.
5. The "yieldPerAcre" field must be a string like "X.XX Tons/Acre". The "estimatedTons" field must equal yieldPerAcre × farmSizeAcres.

Schema:
{
  "plant": "string",
  "farmSizeAcres": number,
  "location": {
    "country": "string",
    "region": "string",
    "currency": "string",
    "currencySymbol": "string",
    "priceSource": "string"
  },
  "timeline": { "daysToHarvest": number, "stages": ["string"] },
  "yield": { "estimatedTons": number, "unit": "Tons", "yieldPerAcre": "string", "note": "string" },
  "financials": {
    "pricePerUnit": "string",
    "priceUnit": "string",
    "marketValueEstimate": "string",
    "fertilizerCostEstimate": "string",
    "laborCostEstimate": "string",
    "totalCostEstimate": "string",
    "netProfit": "string",
    "profitMargin": "string",
    "roi": "string",
    "priceSource": "string"
  },
  "recommendations": ["string"]
}`;

const DIAGNOSE_SYSTEM_PROMPT = `You are an expert plant pathologist AI. Respond with ONLY a valid JSON object.
Schema:
{
  "plant": "string",
  "diseaseName": "string",
  "severity": "Mild" | "Moderate" | "Severe" | "Critical",
  "confidenceScore": "string",
  "cause": "string",
  "treatment": { "organic": ["string"], "chemical": ["string"], "immediateAction": "string" },
  "prevention": ["string"]
}`;

app.post('/api/predict', async (req, res) => {
  const { plant, temperature, humidity, soilType } = req.body;
  if (!plant || !temperature) return res.status(400).json({ error: 'Missing required fields.' });

  try {
    const model = genAI.getGenerativeModel({ 
      model: 'gemma-4-26b-a4b-it',
      generationConfig: { responseMimeType: 'application/json' }
    });
    const userPrompt = `${PREDICT_SYSTEM_PROMPT}\n\nPlant: ${plant}\nTemp: ${temperature}°C\nHumidity: ${humidity || 60}%\nSoil: ${soilType || 'Loam'}\nPredict optimal care.`;
    
    const result = await model.generateContent(userPrompt);
    const parsed = extractJSON(result.response.text());
    res.json(parsed);
  } catch (err) {
    console.error('Gemini Error:', err);
    res.status(500).json({ error: 'Failed to get prediction.' });
  }
});

app.post('/api/yield', async (req, res) => {
  const { plant, farmSizeAcres, temperature, country, region } = req.body;
  console.log(`[API] Received yield request: ${plant} in ${region}, ${country} (${farmSizeAcres} acres)`);
  if (!plant || !farmSizeAcres) return res.status(400).json({ error: 'Missing required fields.' });

  try {
    const model = genAI.getGenerativeModel({ 
      model: 'gemma-4-26b-a4b-it',
      generationConfig: { responseMimeType: 'application/json' }
    });
    const userPrompt = `${YIELD_SYSTEM_PROMPT}\n\nPlant: ${plant}\nFarm Size: ${farmSizeAcres} Acres\nCurrent Temp: ${temperature}°C\nCountry: ${country || 'India'}\nState/Region: ${region || 'Not specified'}\n\nPredict yield, timeline, and financials using REAL market prices for the specified country and region. All monetary values MUST be in the local currency. Cite your price source in the priceSource field.`;
    
    console.log(`[API] Querying Gemini model: gemma-4-26b-a4b-it...`);
    const start = Date.now();
    const result = await model.generateContent(userPrompt);
    const duration = ((Date.now() - start) / 1000).toFixed(1);
    console.log(`[API] AI response received in ${duration}s`);
    
    const parsed = extractJSON(result.response.text());
    console.log(`[API] Successfully parsed and returned JSON`);
    res.json(parsed);
  } catch (err) {
    console.error('Gemini Error:', err);
    res.status(500).json({ error: 'Failed to predict yield.' });
  }
});

app.post('/api/diagnose', async (req, res) => {
  const { plant, symptoms } = req.body;
  if (!plant || !symptoms) return res.status(400).json({ error: 'Missing required fields.' });

  try {
    const model = genAI.getGenerativeModel({ 
      model: 'gemma-4-26b-a4b-it',
      generationConfig: { responseMimeType: 'application/json' }
    });
    const userPrompt = `${DIAGNOSE_SYSTEM_PROMPT}\n\nPlant: ${plant}\nSymptoms: ${symptoms}\nAnalyze the symptoms and provide a detailed diagnosis and treatment plan.`;
    
    const result = await model.generateContent(userPrompt);
    const parsed = extractJSON(result.response.text());
    res.json(parsed);
  } catch (err) {
    console.error('Gemini Error:', err);
    res.status(500).json({ error: 'Failed to diagnose disease.' });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🌱 Agro Backend running on http://localhost:${PORT}`);
});
