import React, { useState, useEffect } from "react";
import PriceChart from "../components/charts/PriceChart.jsx";
import api from "../services/api";

export default function Dashboard() {
  const [selectedCoin, setSelectedCoin] = useState("BTC");
  const [history, setHistory] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState([]);
  const [showPrediction, setShowPrediction] = useState(false);

  // Fetch top assets stats (English names usually come from API)
  useEffect(() => {
    api.get("/prices/top-assets").then(res => setStats(res.data));
  }, []);

  // Fetch price history (OHLCV) when coin changes
  useEffect(() => {
    api.get(`/prices/${selectedCoin}`).then(res => setHistory(res.data));
    setShowPrediction(false); 
  }, [selectedCoin]);

  // Handle Predict Button Click
  const handlePredictClick = async () => {
    const res = await api.get(`/prices/predict/${selectedCoin}`);
    setPredictions(res.data);
    setShowPrediction(true);
  };

  return (
    <div style={{ padding: '20px', color: 'white', background: '#0a0a0a', minHeight: '100vh' }}>
      {/* 1. Updated Main Title */}
      <h2>Smart Trading Dashboard (CIS Project)</h2>
      
      {/* Stats Cards Section */}
      <div style={{ display: 'flex', gap: '15px', marginBottom: '30px' }}>
        {stats.map(s => (
          <div key={s.id} style={{ background: '#1a1a1a', padding: '15px', borderRadius: '8px', flex: 1, borderLeft: '4px solid #3b82f6' }}>
            <span style={{ fontSize: '12px', color: '#888' }}>{s.name}</span>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>
              ${s.price ? s.price.toLocaleString() : "0.00"}
            </div>
          </div>
        ))}
      </div>

      {/* Control Tools */}
      <div style={{ marginBottom: '20px', display: 'flex', gap: '15px' }}>
        <select 
          value={selectedCoin} 
          onChange={(e) => setSelectedCoin(e.target.value)} 
          style={{ padding: '10px', background: '#222', color: 'white', border: '1px solid #444' }}
        >
          <option value="BTC">Bitcoin (BTC)</option>
          <option value="ETH">Ethereum (ETH)</option>
          <option value="BNB">Binance (BNB)</option>
          <option value="SOL">Solana (SOL)</option>
          <option value="DOG">Dogecoin (DOG)</option>
        </select>

        {/* 2. Updated Button Text */}
        <button 
          onClick={handlePredictClick} 
          style={{ padding: '10px 20px', background: '#22c55e', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }}
        >
          Start AI Prediction 🚀
        </button>
      </div>

      <PriceChart historyData={history} predictionData={predictions} showPrediction={showPrediction} />

      {/* Prediction Results Table */}
      {showPrediction && (
        <div style={{ marginTop: '30px', background: '#111', padding: '20px', borderRadius: '10px' }}>
          {/* 3. Updated Section Header */}
          <h3>📋 Prediction Results for {selectedCoin}</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
            <thead>
              <tr style={{ color: '#888', textAlign: 'left', borderBottom: '1px solid #333' }}>
                {/* 4. Updated Table Headers */}
                <th style={{ padding: '10px' }}>Predicted Time</th>
                <th style={{ padding: '10px' }}>Predicted Price</th>
                <th style={{ padding: '10px' }}>Trend</th>
                <th style={{ padding: '10px' }}>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {predictions.map((p, i) => (
                <tr key={i} style={{ borderBottom: '1px solid #222' }}>
                  <td style={{ padding: '10px' }}>{new Date(p.timestamp).toLocaleTimeString('en-US')}</td>
                  <td style={{ padding: '10px', color: '#22c55e' }}>${p.predicted_value}</td>
                  {/* 5. Updated Trend Status (Upward vs Stable) */}
                  <td style={{ padding: '10px' }}>{p.trend === 'Up' ? '🟢 Bullish' : '🟡 Stable'}</td>
                  <td style={{ padding: '10px' }}>{p.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}