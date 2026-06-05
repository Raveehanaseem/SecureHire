import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { Shield, ArrowLeft, User, Mail, Phone, FileText, CheckCircle, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

const STATUS_OPTIONS = ['pending', 'reviewing', 'shortlisted', 'rejected', 'hired']

const STATUS_COLORS = {
  pending: 'badge-gray',
  reviewing: 'badge-gold',
  shortlisted: 'badge-green',
  rejected: 'badge-red',
  hired: 'badge-green',
}

export default function ApplicationsPage() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [jobTitle, setJobTitle] = useState('')

  useEffect(() => {
    if (!user || user.role !== 'employer') { navigate('/login'); return }
    fetchApplications()
    fetchJob()
  }, [jobId])

  const fetchJob = async () => {
    try {
      const { data } = await api.get(`/jobs/${jobId}`)
      setJobTitle(data.title)
    } catch {}
  }

  const fetchApplications = async () => {
    try {
      const { data } = await api.get(`/applications/job/${jobId}`)
      setApplications(data)
    } catch (err) {
      toast.error('Failed to load applications')
    } finally {
      setLoading(false)
    }
  }

  const updateStatus = async (appId, newStatus) => {
    try {
      await api.patch(`/applications/${appId}/status`, { status: newStatus })
      toast.success(`Status updated to ${newStatus}`)
      fetchApplications()
    } catch {
      toast.error('Failed to update status')
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
          <span className="badge badge-gold">Employer</span>
          <button onClick={async () => { await logout(); navigate('/') }}
            className="text-[#8b8ba0] hover:text-white p-2">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-8 py-12">
        <button onClick={() => navigate('/employer')}
          className="flex items-center gap-2 text-[#8b8ba0] hover:text-white mb-8 transition-colors">
          <ArrowLeft size={16} /> Back to Dashboard
        </button>

        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">Applicants</h1>
          <p className="text-[#8b8ba0] text-sm">{jobTitle} · {applications.length} applications</p>
        </div>

        {loading ? (
          <div className="p-8 text-center text-[#8b8ba0]">Loading...</div>
        ) : applications.length === 0 ? (
          <div className="glass-card p-16 text-center text-[#8b8ba0]">
            <User size={40} className="mx-auto mb-4 opacity-30" />
            <p>No applications yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {applications.map((app) => (
              <div key={app.id} className="glass-card p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <div className="w-8 h-8 rounded-full bg-amber-500/20 flex items-center justify-center">
                        <User size={14} className="text-amber-400" />
                      </div>
                      <span className="font-medium">{app.applicant_name}</span>
                      <span className={`badge ${STATUS_COLORS[app.status] || 'badge-gray'}`}>
                        {app.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-[#8b8ba0] mt-2 ml-11">
                      <span className="flex items-center gap-1"><Mail size={11} /> {app.applicant_email}</span>
                      {app.phone && <span className="flex items-center gap-1"><Phone size={11} /> {app.phone}</span>}
                      <span>{new Date(app.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {/* Status Dropdown */}
                  <select
                    value={app.status}
                    onChange={(e) => updateStatus(app.id, e.target.value)}
                    className="secure-input w-36 text-xs"
                    style={{paddingLeft:"12px", background:"#111118", color:"#f8f8f2"}}
                  >
                    {STATUS_OPTIONS.map(s => (
                      <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
                    ))}
                  </select>
                </div>

                {app.cover_letter && (
                  <div className="mt-4 pt-4 border-t border-white/5">
                    <div className="flex items-center gap-2 text-xs text-[#8b8ba0] mb-2">
                      <FileText size={11} />
                      <span>Cover Letter <span className="text-amber-400">(AES-256 decrypted)</span></span>
                    </div>
                    <p className="text-sm text-[#8b8ba0] leading-relaxed">{app.cover_letter}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}