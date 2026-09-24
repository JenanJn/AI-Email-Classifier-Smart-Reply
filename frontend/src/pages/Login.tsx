import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Mail, Lock, User, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(email, password)
      } else {
        await register(name, email, password)
      }
      navigate('/')
    } catch (err: any) {
      const msg = err?.response?.data?.detail
      setError(
        Array.isArray(msg)
          ? msg.map((m: any) => m.msg).join(', ')
          : msg ?? 'Something went wrong. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const fillDemo = () => {
    setEmail('demo@emailai.com')
    setPassword('demo1234')
    setMode('login')
  }

  return (
    <div className="app-shell min-h-screen flex items-center justify-center p-4 md:p-8">
      <div className="w-full max-w-5xl grid lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center">
        {/* Logo */}
        <div className="hidden lg:block px-8">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-12 h-12 rounded-2xl bg-[#e0ad5d] flex items-center justify-center shadow-xl shadow-[#e0ad5d]/10">
              <Brain className="w-6 h-6 text-[#18232a]" />
            </div>
            <div>
              <p className="text-sm font-bold text-[#f5f2ea]">AI Email</p>
              <p className="text-xs text-[#e0ad5d]">Command Center</p>
            </div>
          </div>
          <p className="text-xs uppercase tracking-[0.24em] text-[#e0ad5d] mb-4">Your inbox, clarified</p>
          <h1 className="text-5xl font-bold leading-[1.05] text-[#f5f2ea] max-w-xl">Make every message easier to act on.</h1>
          <p className="text-lg text-[#9caeb0] mt-6 max-w-md leading-relaxed">A calm command center for classification, priority, insights, and replies that sound like you.</p>
          <div className="flex gap-3 mt-10">
            {['Classify', 'Prioritize', 'Reply'].map((item, index) => (
              <div key={item} className="px-3 py-2 rounded-xl border border-[#8ea3a9]/20 bg-[#1b2830]/70 text-xs text-[#c8d0cb]">
                <span className="text-[#e0ad5d] mr-1">0{index + 1}</span> {item}
              </div>
            ))}
          </div>
        </div>

        {/* Card */}
        <div className="card max-w-md w-full mx-auto">
          <div className="lg:hidden text-center mb-7">
            <div className="w-14 h-14 rounded-2xl bg-[#e0ad5d] flex items-center justify-center mx-auto mb-4 shadow-xl shadow-[#e0ad5d]/10">
              <Brain className="w-7 h-7 text-[#18232a]" />
            </div>
            <h1 className="text-2xl font-bold text-[#f5f2ea]">AI Email Command Center</h1>
            <p className="text-[#9caeb0] text-sm mt-1">Intelligent email classification and smart replies</p>
          </div>
          {/* Tab switcher */}
          <div className="flex rounded-xl bg-[#101820] p-1 mb-6">
            {(['login', 'register'] as const).map((m) => (
              <button
                key={m}
                onClick={() => { setMode(m); setError(null) }}
                className={`flex-1 py-2 rounded-md text-sm font-medium transition-all capitalize ${
                  mode === m
                    ? 'bg-[#e0ad5d] text-[#18232a] shadow-sm'
                    : 'text-[#9caeb0] hover:text-[#f5f2ea]'
                }`}
              >
                {m === 'login' ? 'Sign In' : 'Create Account'}
              </button>
            ))}
          </div>

          {/* Error */}
          {error && (
            <div className="flex items-start gap-2 bg-red-500/15 border border-red-500/30 rounded-lg px-3 py-2.5 mb-4">
              <AlertCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div>
                <label className="label">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                    required
                    className="input pl-9"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="label">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="input pl-9"
                />
              </div>
            </div>

            <div>
              <label className="label">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  minLength={4}
                  className="input pl-9 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn-primary py-2.5 text-sm font-semibold flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {mode === 'login' ? 'Signing in...' : 'Creating account...'}
                </span>
              ) : (
                mode === 'login' ? 'Sign In' : 'Create Account'
              )}
            </button>
          </form>

          {/* Demo shortcut */}
          {mode === 'login' && (
            <div className="mt-4 pt-4 border-t border-slate-700">
              <p className="text-xs text-slate-500 text-center mb-2">Quick demo access</p>
              <button
                onClick={fillDemo}
                className="w-full py-2 rounded-lg text-xs font-medium bg-slate-700/50 text-slate-300 hover:bg-slate-700 hover:text-white transition-colors border border-slate-600"
              >
                Use Demo Account
              </button>
            </div>
          )}
        </div>

        <p className="text-center text-xs text-[#65777d] mt-6 lg:col-start-2">
          AI Email Classifier — MCA Mini Project
        </p>
      </div>
    </div>
  )
}

import type React from 'react'
