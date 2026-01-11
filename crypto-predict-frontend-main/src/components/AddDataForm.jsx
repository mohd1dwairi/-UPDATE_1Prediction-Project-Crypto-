import React, { useState } from 'react';
import axios from 'axios';

const AddDataForm = () => {
    const availableCoins = ["BTC", "ETH", "BNB", "SOL", "DOGE"];

    const [formData, setFormData] = useState({
        symbol: 'BTC',
        open: '', high: '', low: '', close: '', volume: '',
        avg_sentiment: 0
    });
    
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState({ type: '', text: '' });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ 
            ...formData, 
            [name]: name === 'symbol' ? value : value 
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        // Validation: Sentiment must be between -1 and 1
        if (formData.avg_sentiment < -1 || formData.avg_sentiment > 1) {
            setStatus({ type: 'error', text: '⚠️ Sentiment must be between -1.0 and 1.0' });
            return;
        }

        setLoading(true);
        setStatus({ type: '', text: '' });

        try {
            const payload = {
                ...formData,
                symbol: formData.symbol.toLowerCase(),
                open: parseFloat(formData.close), // Simplified for demo
                high: parseFloat(formData.close),
                low: parseFloat(formData.close),
                close: parseFloat(formData.close),
                volume: parseFloat(formData.volume || 1000),
                avg_sentiment: parseFloat(formData.avg_sentiment)
            };

            await axios.post('http://localhost:8000/api/prices/add-data', payload);
            setStatus({ type: 'success', text: '✅ Data injected! AI model updated.' });
            
            // Reset sentiment and price
            setFormData({ ...formData, close: '', avg_sentiment: 0 });
        } catch (err) {
            setStatus({ type: 'error', text: '❌ Error: ' + (err.response?.data?.detail || 'Server offline') });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.card}>
            <h3 style={styles.title}>Data Entry & Simulation</h3>
            <p style={styles.subtitle}>Select a coin and set manual sentiment to test AI response.</p>
            
            <form onSubmit={handleSubmit} style={styles.form}>
                <div style={styles.row}>
                    {/* Coin Selection Dropdown */}
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Select Asset</label>
                        <select name="symbol" value={formData.symbol} onChange={handleChange} style={styles.select}>
                            {availableCoins.map(coin => (
                                <option key={coin} value={coin}>{coin}</option>
                            ))}
                        </select>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Market Price ($)</label>
                        <input name="close" type="number" value={formData.close} onChange={handleChange} style={styles.input} placeholder="e.g. 65000" required />
                    </div>
                </div>

                <div style={styles.row}>
                    {/* Sentiment with Min/Max constraints */}
                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Sentiment Score (-1 to 1)</label>
                        <input 
                            name="avg_sentiment" 
                            type="number" 
                            step="0.1" 
                            min="-1" 
                            max="1" 
                            value={formData.avg_sentiment} 
                            onChange={handleChange} 
                            style={styles.input} 
                        />
                        <small style={{color: '#888'}}>Positive: 1.0 | Negative: -1.0</small>
                    </div>

                    <div style={styles.inputGroup}>
                        <label style={styles.label}>Trade Volume</label>
                        <input name="volume" type="number" value={formData.volume} onChange={handleChange} style={styles.input} placeholder="1000" />
                    </div>
                </div>

                <button type="submit" disabled={loading} style={loading ? styles.buttonDisabled : styles.button}>
                    {loading ? 'Processing...' : 'Inject Manual Signal 🚀'}
                </button>
            </form>

            {status.text && (
                <div style={status.type === 'success' ? styles.successBox : styles.errorBox}>
                    {status.text}
                </div>
            )}
        </div>
    );
};

// Professional Styles
const styles = {
    card: { background: '#1a1a1a', padding: '25px', borderRadius: '12px', color: '#fff', border: '1px solid #333' },
    title: { margin: '0 0 5px 0', color: '#3b82f6' },
    subtitle: { fontSize: '13px', color: '#888', marginBottom: '20px' },
    form: { display: 'flex', flexDirection: 'column', gap: '15px' },
    row: { display: 'flex', gap: '15px' },
    inputGroup: { display: 'flex', flexDirection: 'column', flex: 1, gap: '5px' },
    label: { fontSize: '12px', fontWeight: 'bold', color: '#aaa' },
    input: { padding: '10px', borderRadius: '6px', border: '1px solid #444', background: '#222', color: '#fff' },
    select: { padding: '10px', borderRadius: '6px', border: '1px solid #444', background: '#222', color: '#fff', cursor: 'pointer' },
    button: { padding: '12px', background: '#22c55e', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' },
    buttonDisabled: { padding: '12px', background: '#14532d', color: '#aaa', border: 'none', borderRadius: '6px', cursor: 'not-allowed' },
    successBox: { marginTop: '15px', padding: '10px', background: 'rgba(34, 197, 94, 0.2)', color: '#4ade80', borderRadius: '6px', textAlign: 'center' },
    errorBox: { marginTop: '15px', padding: '10px', background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', borderRadius: '6px', textAlign: 'center' }
};

export default AddDataForm;