import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function AdminReports() {
  const [stats, setStats] = useState({});
  const [report, setReport] = useState([]);
  const [trainingLogs, setTrainingLogs] = useState([]); // حالة لتخزين سجلات التدريب

  useEffect(() => {
    // جلب البيانات عند تحميل المكون
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      // جلب الإحصائيات العامة
      const statsRes = await api.get('/admin/stats');
      setStats(statsRes.data);

      // جلب تقرير الدقة (Backtesting)
      const reportRes = await api.get('/admin/accuracy-report');
      setReport(reportRes.data);

      // جلب سجلات تدريب الموديل الجديدة
      const logsRes = await api.get('/admin/training-logs');
      setTrainingLogs(logsRes.data);
    } catch (error) {
      console.error("Error fetching admin reports:", error);
    }
  };

  // وظيفة الطباعة وتصدير PDF
  const handlePrint = () => {
    window.print(); 
  };

  return (
    <div style={styles.reportPage}>
      <h2 style={{borderBottom: '2px solid #3b82f6', paddingBottom: '10px'}}>
        System Performance & Audit 
      </h2>

      {/* --- 1. إحصائيات النظام (Cards) --- */}
      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <p style={styles.label}>Total Users</p>
          <strong>{stats.total_users || 0}</strong>
        </div>
        <div style={styles.statCard}>
          <p style={styles.label}>Market Records</p>
          <strong>{stats.total_data_points || 0}</strong>
        </div>
        <div style={styles.statCard}>
          <p style={styles.label}>AI Forecasts</p>
          <strong>{stats.total_predictions || 0}</strong>
        </div>
      </div>

      <div id="printable-report">
        {/* --- 2. جدول تقرير الدقة (Accuracy Report) --- */}
        <div style={styles.tableContainer}>
          <h3 style={styles.tableTitle}>🎯 AI Model Accuracy Report (Backtesting)</h3>
          <table style={styles.table}>
            <thead>
              <tr style={styles.th}>
                <th>Asset</th>
                <th>Target Time</th>
                <th>Predicted ($)</th>
                <th>Actual ($)</th>
                <th>Accuracy (%)</th>
              </tr>
            </thead>
            <tbody>
              {report.map((item, idx) => (
                <tr key={idx} style={styles.tr}>
                  <td>{item.asset.toUpperCase()}</td>
                  <td>{new Date(item.timestamp).toLocaleString()}</td>
                  <td>{item.predicted_price}</td>
                  <td>{item.actual_price}</td>
                  <td style={{color: item.accuracy > 90 ? '#22c55e' : '#eab308'}}>
                    {item.accuracy}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* --- 3. جدول سجلات التدريب (Training History) - الإضافة الجديدة --- */}
        <div style={{...styles.tableContainer, marginTop: '30px'}}>
          <h3 style={styles.tableTitle}>⚙️ AI Model Training History</h3>
          <table style={styles.table}>
            <thead>
              <tr style={styles.th}>
                <th>Execution Time</th>
                <th>Records Used</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {trainingLogs.map((log, idx) => (
                <tr key={idx} style={styles.tr}>
                  <td>{new Date(log.trained_at).toLocaleString()}</td>
                  <td>{log.records_count} rows</td>
                  <td style={{color: log.status === "Success" ? "#22c55e" : "#f85149", fontWeight: 'bold'}}>
                    {log.status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <button onClick={handlePrint} style={styles.printBtn}>
        Export Full Audit Report to PDF 📄
      </button>
    </div>
  );
}

// التنسيقات البرمجية (Styles)
const styles = {
  reportPage: { padding: '20px', background: '#0d1117', borderRadius: '12px', color: 'white' },
  statsRow: { display: 'flex', gap: '15px', marginBottom: '30px' },
  statCard: { background: '#161b22', padding: '20px', borderRadius: '8px', flex: 1, textAlign: 'center', border: '1px solid #30363d' },
  label: { color: '#8b949e', fontSize: '14px', marginBottom: '5px' },
  tableContainer: { background: '#161b22', padding: '20px', borderRadius: '8px', border: '1px solid #30363d' },
  tableTitle: { color: '#f0f6fc', marginBottom: '15px', fontSize: '18px' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { textAlign: 'left', color: '#8b949e', borderBottom: '1px solid #30363d', padding: '10px' },
  tr: { borderBottom: '1px solid #21262d', height: '45px' },
  printBtn: { marginTop: '30px', padding: '12px 24px', background: '#238636', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold', width: '100%' }
};