import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function AdminReports() {
  const [stats, setStats] = useState({});
  const [reportData, setReportData] = useState([]);

  useEffect(() => {
    // جلب البيانات عند فتح الصفحة
    api.get('/admin/dashboard-stats').then(res => setStats(res.data));
    api.get('/admin/accuracy-analysis').then(res => setReportData(res.data));
  }, []);

  // دالة الطباعة وتصدير PDF (استخدام وظيفة المتصفح الأصلية)
  const handleExportPDF = () => {
    window.print(); 
  };

  return (
    <div className="reports-section">
      <h3>System Overview</h3>
      <div style={styles.grid}>
        <div style={styles.card}>Users: {stats.total_users}</div>
        <div style={styles.card}>Data Rows: {stats.total_records}</div>
        <div style={styles.card}>AI Predictions: {stats.total_predictions}</div>
      </div>

      <div id="printable-table" style={{marginTop: '30px'}}>
        <h3>Accuracy Report (Actual vs. Predicted)</h3>
        <table style={styles.table}>
          <thead>
            <tr>
              <th>Time</th>
              <th>Predicted ($)</th>
              <th>Actual ($)</th>
            </tr>
          </thead>
          <tbody>
            {reportData.map((d, i) => (
              <tr key={i}>
                <td>{new Date(d.timestamp).toLocaleString()}</td>
                <td>{d.predicted_price}</td>
                <td>{d.actual_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <button onClick={handleExportPDF} style={styles.exportBtn}>
        Export Report to PDF 📄
      </button>
    </div>
  );
}

const styles = {
    grid: { display: 'flex', gap: '15px' },
    card: { background: '#1a1a1a', padding: '20px', borderRadius: '8px', flex: 1, border: '1px solid #333' },
    table: { width: '100%', borderCollapse: 'collapse', background: '#111' },
    exportBtn: { marginTop: '20px', padding: '12px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer' }
};