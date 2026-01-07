// src/App.jsx

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// --- 1. استيراد الصفحات الأساسية (الأسهل) ---
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";

// --- 2. تصحيح استيراد صفحة التقارير (المهم جداً لحل الخطأ) ---
// تم تغيير المسار ليطابق شجرة الملفات لديك: src/components/AdminReports.jsx
import AdminReports from "./components/AdminReports.jsx"; 

import AppLayout from "./components/layout/AppLayout.jsx";
import ProtectedRoute from "./routes/ProtectedRoute.jsx";

function App() {
  // جلب رتبة المستخدم من المتصفح للتحقق من الصلاحيات
  const userRole = localStorage.getItem("user_role");

  return (
    <Routes>
      {/* التوجيه التلقائي لصفحة تسجيل الدخول */}
      <Route path="/" element={<Navigate to="/login" replace />} />

      {/* صفحات عامة */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* --- 3. صفحات محمية للمستخدمين والأدمن (متوسط الصعوبة) --- */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />

      {/* --- 4. حماية مسار التقارير للأدمن فقط (الأصعب/الأهم) --- */}
      {/* قمنا بتصحيح المسار ليكون /dashboard/reports كما في الـ Sidebar */}
      <Route
        path="/dashboard/reports"
        element={
          <ProtectedRoute>
            {userRole === "admin" ? (
              <AppLayout>
                <AdminReports />
              </AppLayout>
            ) : (
              // إذا حاول مستخدم عادي الدخول، يتم طرده للداشبورد
              <Navigate to="/dashboard" replace />
            )}
          </ProtectedRoute>
        }
      />

      {/* التعامل مع الروابط الخاطئة */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;