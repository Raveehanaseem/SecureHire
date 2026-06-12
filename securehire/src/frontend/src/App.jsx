import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import LandingPage from './pages/LandingPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import JobsPage from './pages/JobsPage'
import JobDetailPage from "./pages/JobDetailPage.jsx";
import EmployerDashboard from './pages/EmployerDashboard'
import MyApplicationsPage from './pages/MyApplicationsPage'
import ApplicationsPage from './pages/ApplicationsPage'
import AdminDashboard from './pages/AdminDashboard'
import useAuthStore from './hooks/useAuthStore'
import './styles/globals.css'

function ProtectedRoute({ children, allowedRoles }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user?.role)) return <Navigate to="/jobs" replace />
  return children
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#111118',
            color: '#f8f8f2',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: '10px',
            fontSize: '13px',
          },
          success: { iconTheme: { primary: '#10b981', secondary: '#000' } },
          error: { iconTheme: { primary: '#ef4444', secondary: '#000' } },
        }}
      />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/jobs" element={<JobsPage />} />
        <Route path="/my-applications" element={<ProtectedRoute allowedRoles={['applicant']}><MyApplicationsPage /></ProtectedRoute>} />
        <Route path="/my-applications" element={<ProtectedRoute allowedRoles={['applicant']}><MyApplicationsPage /></ProtectedRoute>} />
        <Route path="/jobs/:id" element={<JobDetailPage />} />
        <Route path="/employer/applications/:jobId" element={<ProtectedRoute allowedRoles={['employer']}><ApplicationsPage /></ProtectedRoute>} />
        <Route path="/employer" element={
          <ProtectedRoute allowedRoles={['employer', 'admin']}>
            <EmployerDashboard />
          </ProtectedRoute>
        } />
        <Route path="/admin" element={
          <ProtectedRoute allowedRoles={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}


