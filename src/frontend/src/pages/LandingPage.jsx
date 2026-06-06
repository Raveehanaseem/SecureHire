import { Link } from 'react-router-dom'
import { Shield, Zap, Lock, Users, ChevronRight, CheckCircle } from 'lucide-react'

const stats = [
  { value: "256-bit", label: "AES Encryption" },
  { value: "TLS 1.3", label: "In-Transit Security" },
  { value: "RBAC", label: "Access Control" },
  { value: "JWT", label: "Auth Standard" },
]

const features = [
  { icon: Shield, title: "Zero Trust Architecture", desc: "Every request verified, every data field encrypted. No implicit trust." },
  { icon: Lock, title: "AES-256 Data Protection", desc: "Resumes and personal details encrypted at rest before touching the database." },
  { icon: Zap, title: "Real-Time Events", desc: "Kafka-powered event streaming notifies teams the moment applications arrive." },
  { icon: Users, title: "Role-Based Access", desc: "Strict RBAC — Admins, Employers, and Applicants each see only what they should." },
]

export default function LandingPage() {
  return (
    <div className="mesh-bg min-h-screen">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-white/5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center">
            <Shield size={16} className="text-black" />
          </div>
          <span className="font-semibold text-white tracking-tight">SecureHire</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-ghost text-sm py-2 px-5">Sign In</Link>
          <Link to="/register" className="btn-gold text-sm py-2 px-5">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-5xl mx-auto px-8 pt-24 pb-20 text-center">
        <div className="inline-flex items-center gap-2 badge badge-gold mb-8 animate-fade-up">
          <div className="status-dot bg-amber-400" />
          Enterprise-grade security for recruitment
        </div>

        <h1 className="text-6xl font-bold tracking-tight leading-[1.1] mb-6 animate-fade-up delay-100" style={{fontFamily: "'DM Sans', sans-serif"}}>
          Hire with confidence.<br />
          <span className="gradient-text">Secured by design.</span>
        </h1>

        <p className="text-lg text-[#8b8ba0] max-w-2xl mx-auto mb-10 animate-fade-up delay-200 leading-relaxed">
          SecureHire encrypts every resume, validates every input, and enforces 
          strict role-based access — so your hiring data stays private.
        </p>

        <div className="flex items-center justify-center gap-4 animate-fade-up delay-300">
          <Link to="/register" className="btn-gold flex items-center gap-2">
            Start Hiring <ChevronRight size={16} />
          </Link>
          <Link to="/jobs" className="btn-ghost flex items-center gap-2">
            Browse Jobs <ChevronRight size={16} />
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="max-w-4xl mx-auto px-8 mb-20">
        <div className="glass-card p-1">
          <div className="grid grid-cols-4 divide-x divide-white/5">
            {stats.map((s) => (
              <div key={s.label} className="p-6 text-center">
                <div className="text-2xl font-bold gradient-text mb-1">{s.value}</div>
                <div className="text-xs text-[#8b8ba0] uppercase tracking-widest">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-5xl mx-auto px-8 pb-24">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-3">Security at every layer</h2>
          <p className="text-[#8b8ba0]">Built on OWASP ASVS standards. Verified by design.</p>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="glass-card p-6 hover:border-amber-500/20 transition-all duration-300 group">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center mb-4 group-hover:bg-amber-500/15 transition-colors">
                <Icon size={18} className="text-amber-400" />
              </div>
              <h3 className="font-semibold mb-2 text-white">{title}</h3>
              <p className="text-sm text-[#8b8ba0] leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="max-w-2xl mx-auto px-8 pb-24 text-center">
        <div className="glass-card p-10 glow-gold">
          <h3 className="text-2xl font-bold mb-3">Ready to hire securely?</h3>
          <p className="text-[#8b8ba0] mb-8">Join as an employer or start applying today.</p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/register?role=employer" className="btn-gold">Post a Job</Link>
            <Link to="/register?role=applicant" className="btn-ghost">Apply for Jobs</Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/5 px-8 py-6 text-center text-xs text-[#8b8ba0]">
        SecureHire © 2026 — CYC386 Secure Software Design & Development · COMSATS University Islamabad
      </div>
    </div>
  )
}
