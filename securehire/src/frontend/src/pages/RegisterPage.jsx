import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { Shield, Eye, EyeOff, Lock, Mail, User, Briefcase, AlertCircle, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../hooks/useAuthStore'

const passwordRules = [
  { label: 'At least 8 characters', test: (p) => p.length >= 8 },
  { label: 'One uppercase letter', test: (p) => /[A-Z]/.test(p) },
  { label: 'One number', test: (p) => /\d/.test(p) },
  { label: 'One special character', test: (p) => /[!@#$%^&*]/.test(p) },
]

export default function RegisterPage() {
  const [params] = useSearchParams()
  const navigate = useNavigate()
  const { register, isLoading } = useAuthStore()
  const [form, setForm] = useState({
    email: '',
    password: '',
    full_name: '',
    role: params.get('role') || 'applicant',
  })
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const result = await register(form)
    if (result.success) {
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } else {
      setError(result.error)
    }
  }

  return (
    <div className="mesh-bg min-h-screen flex items-center justify-center px-4 py-12">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-emerald-500/4 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        <div className="text-center mb-8 animate-fade-up">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl bg-amber-500 flex items-center justify-center">
              <Shield size={18} className="text-black" />
            </div>
            <span className="text-xl font-bold tracking-tight">SecureHire</span>
          </Link>
          <h1 className="text-2xl font-bold text-white mb-2">Create account</h1>
          <p className="text-[#8b8ba0] text-sm">Join the secure hiring platform</p>
        </div>

        <div className="glass-card p-8 animate-fade-up delay-100">
          {error && (
            <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-red-400 text-sm">
              <AlertCircle size={16} className="shrink-0" />
              {error}
            </div>
          )}

          <div className="flex rounded-xl overflow-hidden border border-white/8 mb-6">
            {[
              { value: 'applicant', label: 'Job Seeker', icon: User },
              { value: 'employer', label: 'Employer', icon: Briefcase },
            ].map(({ value, label, icon: Icon }) => (
              <button
                key={value}
                type="button"
                onClick={() => setForm({ ...form, role: value })}
                className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-all ${
                  form.role === value
                    ? 'bg-amber-500 text-black'
                    : 'bg-transparent text-[#8b8ba0] hover:text-white'
                }`}
              >
                <Icon size={14} />
                {label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Full Name</label>
              <div className="relative">
                <User size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
                <input
                  type="text"
                  className="secure-input" style={{paddingLeft:"44px"}}
                  placeholder="Raveeha Naseem"
                  value={form.full_name}
                  onChange={(e) => setForm({ ...form, full_name: e.target.value })}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Email</label>
              <div className="relative">
                <Mail size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
                <input
                  type="email"
                  className="secure-input" style={{paddingLeft:"44px"}}
                  placeholder="example@securehire.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">Password</label>
              <div className="relative">
                <Lock size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
                <input
                  type={showPass ? 'text' : 'password'}
                  className="secure-input" style={{paddingLeft:"44px", paddingRight:"44px"}}
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
                <button type="button" onClick={() => setShowPass(!showPass)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8b8ba0] hover:text-white">
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
              {form.password && (
                <div className="mt-3 grid grid-cols-2 gap-1.5">
                  {passwordRules.map(({ label, test }) => (
                    <div key={label} className={`flex items-center gap-1.5 text-xs ${test(form.password) ? 'text-emerald-400' : 'text-[#8b8ba0]'}`}>
                      <CheckCircle size={10} className={test(form.password) ? 'text-emerald-400' : 'text-[#333]'} />
                      {label}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <button type="submit" disabled={isLoading}
              className="btn-gold w-full flex items-center justify-center gap-2 mt-2">
              {isLoading
                ? <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                : 'Create Account'}
            </button>
          </form>

          <div className="divider my-6" />
          <p className="text-center text-sm text-[#8b8ba0]">
            Already have an account?{' '}
            <Link to="/login" className="text-amber-400 hover:text-amber-300 font-medium transition-colors">Sign in</Link>
          </p>
        </div>

        <div className="flex items-center justify-center gap-2 mt-6 text-xs text-[#8b8ba0]">
          <Lock size={11} />
          <span>Your data is encrypted with AES-256</span>
        </div>
      </div>
    </div>
  )
}

