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

  // --- تحسينات إضافية لحساب المقياس تلقائياً لراحة العين ---
  const options = {
    chart: { 
      id: "crypto-chart", 
      background: "#000000", // خلفية سوداء عميقة
      fontFamily: 'Inter, Arial, sans-serif', 
      animations: { enabled: true, easing: 'easeinout', speed: 800 },
      toolbar: {
        show: true,
        tools: {
          download: '<img src="https://img.icons8.com/m_rounded/20/ffffff/download.png" width="15"/>',
          selection: true,
          zoom: true,
          zoomin: true,
          zoomout: true,
          pan: true,
        }
      }
    },
    theme: { mode: "dark" },
    stroke: { 
        width: [1, 3], // سمك خط الشموع مقابل خط التوقع
        dashArray: [0, 8], // خط التوقع سيكون متقطعاً بشكل أنيق
        curve: 'smooth'
    },
    // تحسين الألوان لتكون "Vibrant" وأكثر وضوحاً
    plotOptions: {
      candlestick: {
        colors: { 
          upward: "#00ff88", // أخضر نيون
          downward: "#ff3355" // أحمر زاهي
        },
        wick: { useFillColor: true } // جعل الفتيل بنفس لون الشمعة
      }
    },
    xaxis: { 
      type: "datetime",
      labels: {
        datetimeUTC: false, 
        style: { colors: '#8e8e93', fontSize: '12px' }
      },
      axisBorder: { show: false },
      axisTicks: { show: false }
    },
    yaxis: {
      forceNiceScale: true, // أهم خاصية: لعمل زووم تلقائي على منطقة السعر
      tooltip: { enabled: true },
      labels: {
        formatter: (val) => `$${val.toLocaleString()}`, 
        style: { colors: '#8e8e93', fontSize: '12px' }
      }
    },
    // إضافة خطوط الشبكة (Grid) لتشبه منصات التداول
    grid: {
      borderColor: "#1e1e1e",
      strokeDashArray: 4,
      xaxis: { lines: { show: true } },
      yaxis: { lines: { show: true } }
    },
    tooltip: { 
      shared: true, 
      theme: "dark",
      custom: undefined,
      x: { format: 'dd MMM HH:mm' },
      style: { fontSize: '14px' }
    },
    
    legend: {
      position: 'top',
      horizontalAlign: 'right',
      fontWeight: '400',
      fontSize: '14px',
      markers: { radius: 12 },
      labels: { colors: '#ffffff' },
      offsetY: -10
    },
    // إضافة Crosshair للمساعدة في القراءة
    crosshairs: {
      show: true,
      dropShadow: { enabled: true }
    }
  };

  return (
    <div style={{ 
      background: "#000", 
      padding: "20px", 
      borderRadius: "16px", 
      border: "1px solid #333",
      boxShadow: "0 10px 30px rgba(0,0,0,0.5)" 
    }}>
      <Chart options={options} series={series} type="candlestick" height={450} />
    </div>
  );
}