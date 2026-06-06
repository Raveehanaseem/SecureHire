import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, Plus, Briefcase, Users, CheckCircle, Clock, LogOut, X } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

export default function EmployerDashboard() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '', company: '', description: '', requirements: '',
    location: '', salary_range: '', job_type: 'full_time',
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (!user || user.role !== 'employer') { navigate('/login'); return }
    fetchMyJobs()
  }, [])

  const fetchMyJobs = async () => {
    try {
      // /jobs/my sirf is employer ki jobs laata hai
      const { data } = await api.get('/jobs/my')
      setJobs(data)
    } catch {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const handlePostJob = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await api.post('/jobs/', form)
      toast.success('Job posted! Pending admin approval.')
      setShowForm(false)
      setForm({ title: '', company: '', description: '', requirements: '', location: '', salary_range: '', job_type: 'full_time' })
      fetchMyJobs()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to post job')
    } finally {
      setSubmitting(false)
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
          <button onClick={async () => { await logout(); navigate('/') }} className="text-[#8b8ba0] hover:text-white p-2">
            <LogOut size={16} />
          </button>
        </div>
      </nav>

      <div className="max-w-5xl mx-auto px-8 py-12">
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold mb-1">Employer Dashboard</h1>
            <p className="text-[#8b8ba0] text-sm">Manage your job postings</p>
          </div>
          <button onClick={() => setShowForm(true)} className="btn-gold flex items-center gap-2">
            <Plus size={16} /> Post a Job
          </button>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-10">
          {[
            { label: 'Total Jobs', value: jobs.length, icon: Briefcase, color: 'text-amber-400' },
            { label: 'Active', value: jobs.filter(j => j.is_approved).length, icon: CheckCircle, color: 'text-emerald-400' },
            { label: 'Pending Approval', value: jobs.filter(j => !j.is_approved).length, icon: Clock, color: 'text-[#8b8ba0]' },
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

        <div className="glass-card overflow-hidden">
          <div className="p-6 border-b border-white/5">
            <h2 className="font-semibold">Your Job Postings</h2>
          </div>
          {loading ? (
            <div className="p-8 text-center text-[#8b8ba0]">Loading...</div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center text-[#8b8ba0]">
              <Briefcase size={32} className="mx-auto mb-3 opacity-30" />
              <p>No jobs posted yet. Click "Post a Job" to get started.</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-5 hover:bg-white/2 transition-colors">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{job.title}</span>
                      <span className={`badge ${job.is_approved ? 'badge-green' : 'badge-gray'}`}>
                        {job.is_approved ? 'Active' : 'Pending Approval'}
                      </span>
                    </div>
                    <span className="text-xs text-[#8b8ba0]">{job.location} · {job.job_type}</span>
                  </div>
                  {job.is_approved && <Link to={`/employer/applications/${job.id}`} className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1"><Users size={12} /> View Applicants</Link>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-white/5">
              <h2 className="font-semibold">Post New Job</h2>
              <button onClick={() => setShowForm(false)} className="text-[#8b8ba0] hover:text-white">
                <X size={18} />
              </button>
            </div>
            <form onSubmit={handlePostJob} className="p-6 space-y-5">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Job Title *</label>
                  <input className="secure-input" style={{paddingLeft:"16px"}} placeholder="e.g. Senior Developer"
                    value={form.title} onChange={e => setForm({...form, title: e.target.value})} required />
                </div>
                <div>
                  <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Company *</label>
                  <input className="secure-input" style={{paddingLeft:"16px"}} placeholder="Company name"
                    value={form.company} onChange={e => setForm({...form, company: e.target.value})} required />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Location *</label>
                  <input className="secure-input" style={{paddingLeft:"16px"}} placeholder="e.g. Islamabad, Pakistan"
                    value={form.location} onChange={e => setForm({...form, location: e.target.value})} required />
                </div>
                <div>
                  <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Job Type</label>
                  <select className="secure-input" style={{paddingLeft:"16px", background:"#111118", color:"#f8f8f2"}}
                    value={form.job_type} onChange={e => setForm({...form, job_type: e.target.value})}>
                    <option value="full_time">Full Time</option>
                    <option value="part_time">Part Time</option>
                    <option value="contract">Contract</option>
                    <option value="remote">Remote</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Salary Range</label>
                <input className="secure-input" style={{paddingLeft:"16px"}} placeholder="e.g. PKR 80,000 - 120,000"
                  value={form.salary_range} onChange={e => setForm({...form, salary_range: e.target.value})} />
              </div>
              <div>
                <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Description *</label>
                <textarea className="secure-input min-h-[100px] resize-none" style={{paddingLeft:"16px"}}
                  placeholder="Describe the role..." value={form.description}
                  onChange={e => setForm({...form, description: e.target.value})} required />
              </div>
              <div>
                <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Requirements *</label>
                <textarea className="secure-input min-h-[80px] resize-none" style={{paddingLeft:"16px"}}
                  placeholder="Required skills and experience..." value={form.requirements}
                  onChange={e => setForm({...form, requirements: e.target.value})} required />
              </div>
              <div className="flex gap-3 pt-2">
                <button type="button" onClick={() => setShowForm(false)} className="btn-ghost flex-1">Cancel</button>
                <button type="submit" disabled={submitting} className="btn-gold flex-1 flex items-center justify-center">
                  {submitting ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : 'Post Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
