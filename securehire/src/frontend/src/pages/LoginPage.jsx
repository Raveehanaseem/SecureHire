import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Shield, Eye, EyeOff, Lock, Mail, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'
import useAuthStore from '../hooks/useAuthStore'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login, isLoading } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!form.email || !form.password) {
      setError('Please fill in all fields')
      return
    }
    const result = await login(form.email, form.password)
    if (result.success) {
      toast.success('Welcome back!')
      const role = result.role
      if (role === 'admin') navigate('/admin')
      else if (role === 'employer') navigate('/employer')
      else navigate('/jobs')
    } else {
      setError(result.error)
    }
  }

  return (
    <div className="mesh-bg min-h-screen flex items-center justify-center px-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md relative">
        <div className="text-center mb-8 animate-fade-up">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl bg-amber-500 flex items-center justify-center">
              <Shield size={18} className="text-black" />
            </div>
            <span className="text-xl font-bold tracking-tight">SecureHire</span>
          </Link>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome back</h1>
          <p className="text-[#8b8ba0] text-sm">Sign in to your account</p>
        </div>

        <div className="glass-card p-8 animate-fade-up delay-100">
          {error && (
            <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4 mb-6 text-red-400 text-sm">
              <AlertCircle size={16} className="shrink-0" />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
                <input
                  type="email"
                  className="secure-input" style={{paddingLeft:"44px"}}
                  placeholder="example@securehire.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs text-[#8b8ba0] uppercase tracking-widest mb-2">
                Password
              </label>
              <div className="relative">
                <Lock size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#8b8ba0]" />
                <input
                  type={showPass ? 'text' : 'password'}
                  className="secure-input" style={{paddingLeft:"44px", paddingRight:"44px"}}
                  placeholder="Enter your password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-[#8b8ba0] hover:text-white transition-colors"
                  onClick={() => setShowPass(!showPass)}
                >
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-gold w-full flex items-center justify-center gap-2 mt-2"
            >
              {isLoading ? (
                <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
              ) : 'Sign In'}
            </button>
          </form>

          <div className="divider my-6" />

          <p className="text-center text-sm text-[#8b8ba0]">
            Don't have an account?{' '}
            <Link to="/register" className="text-amber-400 hover:text-amber-300 font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>

        <div className="flex items-center justify-center gap-2 mt-6 text-xs text-[#8b8ba0]">
          <Lock size={11} />
          <span>Protected by TLS 1.3 · JWT Authentication</span>
        </div>
      </div>
    </div>
  )
}

