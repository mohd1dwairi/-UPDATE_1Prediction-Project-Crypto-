import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import api from "../../services/api"; // التأكد من استيراد ملف الإعدادات الخاص بـ Axios

// القائمة الأساسية لجميع المستخدمين
const navItems = [
  { label: "Overview", path: "/dashboard" },
];

export default function Sidebar() {
  const [isTraining, setIsTraining] = useState(false); // حالة لمراقبة عملية التدريب
  const userRole = localStorage.getItem("user_role"); // جلب صلاحية المستخدم من التخزين المحلي

  // دالة استدعاء مسار إعادة التدريب من الباك إيند
  const handleRetrain = async () => {
    const confirmAction = window.confirm("Are you sure? This will retrain the AI using all 125,000+ records.");
    if (!confirmAction) return;

    setIsTraining(true);
    try {
      // إرسال طلب POST إلى المسار الذي قمنا بإنشائه في FastAPI
      const response = await api.post("/admin/retrain");
      alert(response.data.message); // إظهار رسالة النجاح القادمة من السيرفر
    } catch (error) {
      console.error("Retraining error:", error);
      alert("Failed to start retraining. Check server connection.");
    } finally {
      setIsTraining(false); // إعادة الزر لحالته الطبيعية
    }
  };

  return (
    <aside className="sidebar">
      {/* هوية المشروع */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">₿</div>
        <div>
          <p className="sidebar-title">Crypto Predict</p>
          <p className="sidebar-subtitle">AI Insights</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {/* روابط التنقل العادية */}
        {navItems.map((item) => (
          <NavLink
            key={item.label}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "nav-item-active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}

        {/* أدوات الإدارة - تظهر فقط للأدمن */}
        {userRole === "admin" && (
          <>
            {/* فاصل بصري بين روابط المستخدم وأدوات الإدارة */}
            <div style={{ margin: "20px 0", borderTop: "1px solid #30363d", opacity: 0.5 }}></div>
            
            {/* رابط صفحة التقارير */}
            <NavLink
              to="/dashboard/reports"
              className={({ isActive }) =>
                `nav-item admin-link ${isActive ? "nav-item-active" : ""}`
              }
            >
              📊 Reports & Analytics
            </NavLink>

            {/* زر إعادة التدريب المباشر */}
            <button
              onClick={handleRetrain}
              disabled={isTraining}
              className={`nav-item retrain-btn ${isTraining ? "loading" : ""}`}
              style={{
                width: "100%",
                textAlign: "left",
                background: "transparent",
                border: "none",
                cursor: isTraining ? "not-allowed" : "pointer",
                color: isTraining ? "#8b949e" : "#ff9800" // لون برتقالي لتمييز زر التدريب
              }}
            >
              {isTraining ? "🔄 Training AI..." : "🚀 Retrain AI Model"}
            </button>
          </>
        )}
      </nav>
    </aside>
  );
}