import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, MapPin, Clock, Briefcase, Search, Filter, ChevronRight, LogOut } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../utils/api'
import useAuthStore from '../hooks/useAuthStore'

const JOB_TYPE_LABELS = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  remote: 'Remote',
}

export default function JobsPage() {
  const { user, isAuthenticated, logout } = useAuthStore()
  const navigate = useNavigate()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetchJobs()
  }, [])

  const fetchJobs = async () => {
    try {
      const { data } = await api.get('/jobs/')
      setJobs(data)
    } catch {
      toast.error('Failed to load jobs')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const filtered = jobs.filter((j) => {
    const matchSearch = j.title.toLowerCase().includes(search.toLowerCase()) ||
      j.company.toLowerCase().includes(search.toLowerCase()) ||
      j.location.toLowerCase().includes(search.toLowerCase())
    const matchFilter = filter === 'all' || j.job_type === filter
    return matchSearch && matchFilter
  })

  return (
    <div className="mesh-bg min-h-screen">
      {/* Nav */}
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
              {user?.role === 'applicant' && (<Link to="/my-applications" className="btn-ghost text-sm py-2 px-4">My Applications</Link>)}{user?.role === 'employer' && (
                <Link to="/employer" className="btn-gold text-sm py-2 px-4">Dashboard</Link>
              )}
              {user?.role === 'admin' && (
                <Link to="/admin" className="btn-gold text-sm py-2 px-4">Admin</Link>
              )}
              <button onClick={handleLogout} className="text-[#8b8ba0] hover:text-white transition-colors p-2">
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

      <div className="max-w-4xl mx-auto px-8 py-12">
        {/* Header */}
        <div className="mb-10 animate-fade-up">
          <h1 className="text-4xl font-bold mb-3">
            Find your next <span className="gradient-text">secure</span> role
          </h1>
          <p className="text-[#8b8ba0]">{jobs.length} open positions · All data encrypted end-to-end</p>
        </div>

        {/* Search & Filter */}
        <div className="flex gap-3 mb-8 animate-fade-up delay-100">
          <div className="flex-1 relative">
            <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
            <input
              className="secure-input pl-11"
              placeholder="Search jobs, companies, locations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            className="secure-input w-40"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="full_time">Full Time</option>
            <option value="part_time">Part Time</option>
            <option value="contract">Contract</option>
            <option value="remote">Remote</option>
          </select>
        </div>

        {/* Jobs List */}
        {loading ? (
          <div className="space-y-3">
            {[1,2,3].map(i => (
              <div key={i} className="glass-card p-6 animate-pulse">
                <div className="h-5 bg-white/5 rounded w-1/3 mb-3" />
                <div className="h-4 bg-white/5 rounded w-1/4 mb-4" />
                <div className="h-3 bg-white/5 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="glass-card p-16 text-center text-[#8b8ba0]">
            <Briefcase size={40} className="mx-auto mb-4 opacity-30" />
            <p>No jobs found matching your search</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((job, i) => (
              <div
                key={job.id}
                className="glass-card p-6 hover:border-amber-500/20 transition-all duration-200 cursor-pointer group animate-fade-up"
                style={{ animationDelay: `${i * 0.05}s`, opacity: 0 }}
                onClick={() => navigate(`/jobs/${job.id}`)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-white group-hover:text-amber-300 transition-colors">
                        {job.title}
                      </h3>
                      <span className="badge badge-gold">{JOB_TYPE_LABELS[job.job_type] || job.job_type}</span>
                    </div>
                    <p className="text-[#8b8ba0] text-sm font-medium mb-3">{job.company}</p>
                    <div className="flex items-center gap-4 text-xs text-[#8b8ba0]">
                      <span className="flex items-center gap-1.5">
                        <MapPin size={11} /> {job.location}
                      </span>
                      {job.salary_range && (
                        <span className="flex items-center gap-1.5">
                          <Briefcase size={11} /> {job.salary_range}
                        </span>
                      )}
                      <span className="flex items-center gap-1.5">
                        <Clock size={11} /> {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <ChevronRight size={16} className="text-[#8b8ba0] group-hover:text-amber-400 transition-colors mt-1" />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}


