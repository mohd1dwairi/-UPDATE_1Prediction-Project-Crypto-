import React from "react";
import Chart from "react-apexcharts";

export default function PriceChart({ historyData, predictionData, showPrediction }) {
  
  // 1. Preparing the Data Series
  const series = [
    {
      name: "Price History (OHLCV)", // اسم السلسلة التاريخية
      type: "candlestick",
      data: historyData 
    }
  ];

  // 2. Add AI Prediction Line if enabled
  if (showPrediction && predictionData.length > 0) {
    series.push({
      name: "AI Prediction", // اسم سلسلة التوقع
      type: "line",
      data: predictionData.map(p => ({
        x: new Date(p.timestamp).getTime(),
        y: p.predicted_value
      }))
    });
  }

  const options = {
    chart: { 
      id: "crypto-chart", 
      background: "transparent",
      fontFamily: 'Inter, Arial, sans-serif', // استخدام خطوط واضحة
      toolbar: {
        show: true,
        tools: {
          download: true,
          selection: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
        }
      }
    },
    theme: { mode: "dark" },
    xaxis: { 
      type: "datetime",
      labels: {
        datetimeUTC: false, // لعرض الوقت حسب التوقيت المحلي للمستخدم
        style: { colors: '#888' }
      }
    },
    yaxis: {
      labels: {
        formatter: (val) => `$${val.toLocaleString()}`, // إضافة علامة الدولار لمحور السعر
        style: { colors: '#888' }
      }
    },
    stroke: { 
        width: [1, 3], 
        dashArray: [0, 5] // الخط الثاني (التوقع) سيكون متقطعاً
    },
    plotOptions: {
      candlestick: {
        colors: { 
          upward: "#22c55e", 
          downward: "#ef4444" 
        }
      }
    },
    tooltip: { 
      shared: true, 
      theme: "dark",
      x: { format: 'dd MMM yyyy HH:mm' } // تنسيق التاريخ في التول تيب
    },
    legend: {
      position: 'top',
      horizontalAlign: 'center',
      labels: { colors: '#fff' }
    }
  };

  return (
    <div style={{ background: "#111", padding: "10px", borderRadius: "10px" }}>
      <Chart options={options} series={series} type="candlestick" height={350} />
    </div>
  );
}