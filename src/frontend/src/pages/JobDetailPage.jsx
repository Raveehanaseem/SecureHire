import { useState, useEffect } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { Shield, MapPin, Clock, Briefcase, ArrowLeft, Send, Phone, FileText, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

export default function JobDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user, isAuthenticated, logout } = useAuthStore()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)
  const [applying, setApplying] = useState(false)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ cover_letter: '', phone: '' })
  const [applied, setApplied] = useState(false)

  useEffect(() => {
    fetchJob()
  }, [id])

  const fetchJob = async () => {
    try {
      const { data } = await api.get(`/jobs/${id}`)
      setJob(data)
    } catch {
      toast.error('Job not found')
      navigate('/jobs')
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async (e) => {
    e.preventDefault()
    setApplying(true)
    try {
      await api.post('/applications/', {
        job_id: id,
        cover_letter: form.cover_letter,
        phone: form.phone,
      })
      toast.success('Application submitted successfully!')
      setApplied(true)
      setShowForm(false)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to apply')
    } finally {
      setApplying(false)
    }
  }

  if (loading) return (
    <div className="mesh-bg min-h-screen flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
    </div>
  )

  if (!job) return null

  return (
    <div className="mesh-bg min-h-screen">
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/5 sticky top-0 bg-[#050507]/80 backdrop-blur-xl z-50">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center">
            <Shield size={14} className="text-black" />
          </div>
          <span className="font-semibold text-white">SecureHire</span>
        </Link>
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="text-sm text-[#8b8ba0]">{user?.full_name}</span>
              <span className="badge badge-gold">{user?.role}</span>
              <button onClick={async () => { await logout(); navigate('/') }}
                className="text-[#8b8ba0] hover:text-white p-2">
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost text-sm py-2 px-4">Sign In</Link>
              <Link to="/register" className="btn-gold text-sm py-2 px-4">Get Started</Link>
            </>
          )}
        </div>
      </nav>

      <div className="max-w-3xl mx-auto px-8 py-12">
        <button onClick={() => navigate('/jobs')}
          className="flex items-center gap-2 text-[#8b8ba0] hover:text-white mb-8 transition-colors">
          <ArrowLeft size={16} /> Back to Jobs
        </button>

        <div className="glass-card p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white mb-2">{job.title}</h1>
              <p className="text-amber-400 font-medium mb-4">{job.company}</p>
              <div className="flex flex-wrap items-center gap-4 text-sm text-[#8b8ba0]">
                <span className="flex items-center gap-1.5"><MapPin size={13} /> {job.location}</span>
                <span className="flex items-center gap-1.5"><Briefcase size={13} /> {job.job_type?.replace('_', ' ')}</span>
                {job.salary_range && <span className="flex items-center gap-1.5">💰 {job.salary_range}</span>}
                <span className="flex items-center gap-1.5"><Clock size={13} /> {new Date(job.created_at).toLocaleDateString()}</span>
              </div>
            </div>
            {job.deadline && (
              <div className="text-right">
                <p className="text-xs text-[#8b8ba0]">Deadline</p>
                <p className="text-sm text-red-400">{new Date(job.deadline).toLocaleDateString()}</p>
              </div>
            )}
          </div>

          <div className="border-t border-white/5 pt-6 mb-6">
            <h2 className="font-semibold mb-3">Job Description</h2>
            <p className="text-[#8b8ba0] text-sm leading-relaxed whitespace-pre-line">{job.description}</p>
          </div>

          <div className="border-t border-white/5 pt-6 mb-8">
            <h2 className="font-semibold mb-3">Requirements</h2>
            <p className="text-[#8b8ba0] text-sm leading-relaxed whitespace-pre-line">{job.requirements}</p>
          </div>

          {/* Apply Button */}
          {user?.role === 'applicant' && !applied && (
            <button onClick={() => setShowForm(true)}
              className="btn-gold flex items-center gap-2 w-full justify-center">
              <Send size={16} /> Apply Now
            </button>
          )}
          {applied && (
            <div className="flex items-center justify-center gap-2 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-400">
              ✓ Application Submitted Successfully
            </div>
          )}
          {!isAuthenticated && (
            <Link to="/login" className="btn-gold flex items-center gap-2 w-full justify-center">
              Sign in to Apply
            </Link>
          )}
          {user?.role === 'employer' && (
            <div className="p-4 bg-white/3 rounded-xl text-center text-[#8b8ba0] text-sm">
              Employers cannot apply to jobs
            </div>
          )}
        </div>
      </div>

      {/* Apply Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="glass-card w-full max-w-lg">
            <div className="flex items-center justify-between p-6 border-b border-white/5">
              <h2 className="font-semibold">Apply — {job.title}</h2>
              <button onClick={() => setShowForm(false)} className="text-[#8b8ba0] hover:text-white">✕</button>
            </div>
            <form onSubmit={handleApply} className="p-6 space-y-5">
              <div>
                <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">
                  <Phone size={11} className="inline mr-1" /> Phone Number
                </label>
                <input
                  className="secure-input" style={{paddingLeft:"16px"}}
                  placeholder="+92 300 1234567"
                  value={form.phone}
                  onChange={e => setForm({...form, phone: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">
                  <FileText size={11} className="inline mr-1" /> Cover Letter
                  <span className="text-amber-400 ml-1">(encrypted with AES-256)</span>
                </label>
                <textarea
                  className="secure-input min-h-[140px] resize-none" style={{paddingLeft:"16px"}}
                  placeholder="Tell the employer why you're a great fit..."
                  value={form.cover_letter}
                  onChange={e => setForm({...form, cover_letter: e.target.value})}
                />
              </div>
              <div className="flex gap-3">
                <button type="button" onClick={() => setShowForm(false)} className="btn-ghost flex-1">Cancel</button>
                <button type="submit" disabled={applying} className="btn-gold flex-1 flex items-center justify-center gap-2">
                  {applying
                    ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                    : <><Send size={14} /> Submit Application</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}