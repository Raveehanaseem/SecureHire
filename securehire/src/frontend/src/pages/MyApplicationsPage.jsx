import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, Briefcase, Clock, CheckCircle, XCircle, LogOut, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

const STATUS_COLORS = {
  pending: 'badge-gray',
  reviewing: 'badge-gold',
  shortlisted: 'badge-green',
  rejected: 'badge-red',
  hired: 'badge-green',
}

const STATUS_ICONS = {
  pending: Clock,
  reviewing: Clock,
  shortlisted: CheckCircle,
  rejected: XCircle,
  hired: CheckCircle,
}

export default function MyApplicationsPage() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || user.role !== 'applicant') { navigate('/login'); return }
    fetchApplications()
  }, [])

  const fetchApplications = async () => {
    try {
      const { data } = await api.get('/applications/my')
      setApplications(data)
    } catch {
      toast.error('Failed to load applications')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mesh-bg min-h-screen">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/5 sticky top-0 bg-[#050507]/80 backdrop-blur-xl z-50">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center">
            <Shield size={14} className="text-black" />
          </div>
          <span className="font-semibold">SecureHire</span>
        </Link>
        <div className="flex items-center gap-3">
          <span className="text-sm text-[#8b8ba0]">{user?.full_name}</span>
          <span className="badge badge-gold">Applicant</span>
          <Link to="/jobs" className="btn-ghost text-sm py-2 px-4">Browse Jobs</Link>
          <button onClick={async () => { await logout(); navigate('/') }}
            className="text-[#8b8ba0] hover:text-white p-2">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-8 py-12">
        <button onClick={() => navigate('/jobs')}
          className="flex items-center gap-2 text-[#8b8ba0] hover:text-white mb-8 transition-colors">
          <ArrowLeft size={16} /> Back to Jobs
        </button>

        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">My Applications</h1>
          <p className="text-[#8b8ba0] text-sm">{applications.length} total applications</p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-[#8b8ba0]">Loading...</div>
        ) : applications.length === 0 ? (
          <div className="glass-card p-16 text-center text-[#8b8ba0]">
            <Briefcase size={40} className="mx-auto mb-4 opacity-30" />
            <p className="mb-4">No applications yet</p>
            <Link to="/jobs" className="btn-gold text-sm py-2 px-6">Browse Jobs</Link>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map((app) => {
              const Icon = STATUS_ICONS[app.status] || Clock
              return (
                <div key={app.id} className="glass-card p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                          <Briefcase size={14} className="text-amber-400" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{app.job_title}</p>
                          <p className="text-xs text-[#8b8ba0]">{app.company}</p>
                        </div>
                      </div>
                      <p className="text-xs text-[#8b8ba0] mt-2 ml-11">
                        Applied: {new Date(app.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Icon size={14} className={app.status === 'shortlisted' || app.status === 'hired' ? 'text-emerald-400' : app.status === 'rejected' ? 'text-red-400' : 'text-[#8b8ba0]'} />
                      <span className={`badge ${STATUS_COLORS[app.status] || 'badge-gray'}`}>
                        {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}