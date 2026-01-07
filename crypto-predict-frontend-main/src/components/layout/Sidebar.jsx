import React from "react";
import { NavLink } from "react-router-dom";

// --- 1. تعريف العناصر الأساسية (الأسهل) ---
// هذه القائمة تظهر لجميع المستخدمين (Admin & User)
const navItems = [
  { label: "Overview", path: "/dashboard" },
  { label: "Markets", path: "/dashboard/markets" },
  { label: "Predictions", path: "/dashboard/predictions" },
  { label: "Sentiment", path: "/dashboard/sentiment" },
  { label: "Settings", path: "/dashboard/settings" },
];

export default function Sidebar() {
  // --- 2. جلب الصلاحيات (متوسط الصعوبة) ---
  // نقرأ الرتبة المخزنة في localStorage عند تسجيل الدخول
  const userRole = localStorage.getItem("user_role");

  return (
    <aside className="sidebar">
      {/* شعار المشروع وهويته البصرية */}
      <div className="sidebar-brand">
        <div className="sidebar-logo">₿</div>
        <div>
          <p className="sidebar-title">Crypto Predict</p>
          <p className="sidebar-subtitle">AI Insights</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {/* --- 3. عرض العناصر الأساسية عبر دالة الخارطة (Map) --- */}
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

        {/* --- 4. التحقق البرمجي لإظهار التقارير (الأصعب/الأهم) --- */}
        {/* هذا الجزء يظهر فقط إذا كانت القيمة المخزنة هي "admin" */}
        {userRole === "admin" && (
          <NavLink 
            to="/dashboard/reports" 
            className={({ isActive }) =>
              `nav-item admin-link ${isActive ? "nav-item-active" : ""}`
            }
            style={{ marginTop: '20px', borderTop: '1px solid #30363d', paddingTop: '15px' }}
          >
            📊 Reports & Analytics
          </NavLink>
        )}
      </nav>
    </aside>
  );
}