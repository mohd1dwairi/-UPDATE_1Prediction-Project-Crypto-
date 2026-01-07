import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function AdminReports() {
  const [stats, setStats] = useState({});
  const [report, setReport] = useState([]);

  useEffect(() => {
    // جلب الإحصائيات والتقارير عند تحميل المكون
    api.get('/admin/stats').then(res => setStats(res.data));
    api.get('/admin/accuracy-analysis').then(res => setReport(res.data));
  }, []);

  // وظيفة الطباعة وتصدير PDF
  const handlePrint = () => {
    window.print(); // سيقوم المتصفح تلقائياً بتحويل الصفحة الحالية لـ PDF
  };

  return (
    <div style={styles.reportPage}>
      <h2 style={{borderBottom: '2px solid #3b82f6'}}>System Performance & Audit</h2>

      {/* إحصائيات النظام */}
      <div style={styles.statsRow}>
        <div style={styles.statCard}>Users: <strong>{stats.total_users}</strong></div>
        <div style={styles.statCard}>Market Records: <strong>{stats.total_data_points}</strong></div>
        <div style={styles.statCard}>AI Forecasts: <strong>{stats.total_predictions}</strong></div>
      </div>

      {/* جدول تقرير الدقة - Backtesting */}
      <div id="printable-report" style={styles.tableContainer}>
        <h3>AI Model Accuracy Report</h3>
        <table style={styles.table}>
          <thead>
            <tr style={styles.th}>
              <th>Asset</th>
              <th>Target Time</th>
              <th>AI Predicted ($)</th>
              <th>Actual Market ($)</th>
              <th>Accuracy (%)</th>
            </tr>
          </thead>
          <tbody>
            {report.map((item, idx) => {
              const accuracy = (100 - (Math.abs(item.actual_price - item.predicted_price) / item.actual_price * 100)).toFixed(2);
              return (
                <tr key={idx} style={styles.tr}>
                  <td>{item.asset.toUpperCase()}</td>
                  <td>{new Date(item.timestamp).toLocaleString()}</td>
                  <td>{item.predicted_price}</td>
                  <td>{item.actual_price}</td>
                  <td style={{color: accuracy > 90 ? '#22c55e' : '#eab308'}}>{accuracy}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <button onClick={handlePrint} style={styles.printBtn}>
        Export Full Report to PDF 📄
      </button>
    </div>
  );
}

const styles = {
  reportPage: { padding: '20px', background: '#0d1117', borderRadius: '12px' },
  statsRow: { display: 'flex', gap: '15px', marginBottom: '30px' },
  statCard: { background: '#161b22', padding: '20px', borderRadius: '8px', flex: 1, textAlign: 'center', border: '1px solid #30363d' },
  tableContainer: { background: '#161b22', padding: '20px', borderRadius: '8px' },
  table: { width: '100%', borderCollapse: 'collapse', marginTop: '15px' },
  th: { textAlign: 'left', color: '#8b949e', borderBottom: '1px solid #30363d' },
  tr: { borderBottom: '1px solid #21262d' },
  printBtn: { marginTop: '20px', padding: '12px 24px', background: '#238636', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }
};