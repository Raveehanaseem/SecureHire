import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, CheckCircle, Briefcase, Activity, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

export default function AdminDashboard() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [allJobs, setAllJobs] = useState([])
  const [pendingJobs, setPendingJobs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user || user.role !== 'admin') { navigate('/login'); return }
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      // All approved jobs
      const { data: approved } = await api.get('/jobs/')
      // Pending jobs
      const { data: pending } = await api.get('/jobs/pending')
      setAllJobs([...approved, ...pending])
      setPendingJobs(pending)
    } catch (err) {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const approveJob = async (jobId) => {
    try {
      await api.patch(`/jobs/${jobId}/approve`)
      toast.success('Job approved!')
      fetchJobs()
    } catch {
      toast.error('Failed to approve')
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
          <span className="badge badge-red">Admin</span>
          <span className="text-sm text-[#8b8ba0]">{user?.full_name}</span>
          <button onClick={async () => { await logout(); navigate('/') }} className="text-[#8b8ba0] hover:text-white p-2">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="mb-10">
          <h1 className="text-3xl font-bold mb-1">Admin Dashboard</h1>
          <p className="text-[#8b8ba0] text-sm">Platform management · RBAC enforced</p>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-10">
          {[
            { label: 'Total Jobs', value: allJobs.length, icon: Briefcase, color: 'text-amber-400' },
            { label: 'Pending Approval', value: pendingJobs.length, icon: Activity, color: 'text-red-400' },
            { label: 'Active Jobs', value: allJobs.filter(j => j.is_approved).length, icon: CheckCircle, color: 'text-emerald-400' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="glass-card p-6">
              <div className="flex items-center gap-3 mb-2">
                <Icon size={18} className={color} />
                <span className="text-xs text-[#8b8ba0] uppercase tracking-widest">{label}</span>
              </div>
              <div className="text-3xl font-bold">{value}</div>
            </div>
          ))}
        </div>

        {/* Pending Jobs */}
        <div className="glass-card overflow-hidden mb-6">
          <div className="p-6 border-b border-white/5 flex items-center justify-between">
            <h2 className="font-semibold">Pending Job Approvals</h2>
            {pendingJobs.length > 0 && (
              <span className="badge badge-red">{pendingJobs.length} pending</span>
            )}
          </div>
          {loading ? (
            <div className="p-8 text-center text-[#8b8ba0]">Loading...</div>
          ) : pendingJobs.length === 0 ? (
            <div className="p-10 text-center text-[#8b8ba0]">
              <CheckCircle size={28} className="mx-auto mb-3 opacity-30 text-emerald-400" />
              <p>All jobs approved</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {pendingJobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-5">
                  <div>
                    <p className="font-medium text-sm mb-1">{job.title}</p>
                    <p className="text-xs text-[#8b8ba0]">{job.company} · {job.location}</p>
                  </div>
                  <button
                    onClick={() => approveJob(job.id)}
                    className="btn-gold text-xs py-2 px-4 flex items-center gap-1.5"
                  >
                    <CheckCircle size={12} /> Approve
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* All Jobs */}
        <div className="glass-card overflow-hidden">
          <div className="p-6 border-b border-white/5">
            <h2 className="font-semibold">All Job Listings</h2>
          </div>
          <div className="divide-y divide-white/5">
            {allJobs.map((job) => (
              <div key={job.id} className="flex items-center justify-between p-5">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm">{job.title}</span>
                    <span className={`badge ${job.is_approved ? 'badge-green' : 'badge-gray'}`}>
                      {job.is_approved ? 'Approved' : 'Pending'}
                    </span>
                  </div>
                  <p className="text-xs text-[#8b8ba0]">{job.company} · {job.location}</p>
                </div>
                <span className="text-xs text-[#8b8ba0]">{new Date(job.created_at).toLocaleDateString()}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}