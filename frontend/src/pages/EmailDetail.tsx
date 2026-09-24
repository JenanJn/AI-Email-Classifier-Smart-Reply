import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Mail, Clock, User, AtSign,
  RefreshCw, Trash2, AlertCircle,
} from 'lucide-react'
import { emailsApi } from '../api/emails'
import type { Email, Reply } from '../types'
import AIInsightPanel from '../components/analysis/AIInsightPanel'
import ReplyEditor from '../components/reply/ReplyEditor'
import { formatDateTime } from '../utils/dateFormat'
import CategoryBadge from '../components/email/CategoryBadge'
import PriorityBadge from '../components/email/PriorityBadge'

export default function EmailDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [email, setEmail] = useState<Email | null>(null)
  const [loading, setLoading] = useState(true)
  const [reanalyzing, setReanalyzing] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    load()
  }, [id])

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await emailsApi.get(id!)
      setEmail(data)
    } catch {
      setError('Could not load this email.')
    } finally {
      setLoading(false)
    }
  }

  const handleReanalyze = async () => {
    setReanalyzing(true)
    try {
      const data = await emailsApi.analyze(id!)
      setEmail(data)
    } catch {
      setError('Re-analysis failed.')
    } finally {
      setReanalyzing(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Delete this email? This cannot be undone.')) return
    setDeleting(true)
    try {
      await emailsApi.delete(id!)
      navigate('/inbox')
    } catch {
      setError('Could not delete email.')
      setDeleting(false)
    }
  }

  const handleReplyUpdate = (reply: Reply) => {
    setEmail((prev) => prev ? { ...prev, reply } : prev)
  }

  if (loading) return <DetailSkeleton />

  if (error || !email) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4 p-6">
        <AlertCircle className="w-10 h-10 text-red-400" />
        <p className="text-slate-400">{error ?? 'Email not found'}</p>
        <button onClick={() => navigate('/inbox')} className="btn-secondary">
          Back to Inbox
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-full bg-slate-900">
      {/* Top bar */}
      <div className="sticky top-0 z-10 px-6 py-3 border-b border-slate-800 bg-slate-900 flex items-center justify-between gap-4">
        <button
          onClick={() => navigate('/inbox')}
          className="btn-ghost flex items-center gap-1.5 text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-2">
          {email.is_analyzed && email.analysis && (
            <>
              <PriorityBadge level={email.analysis.priority_level} score={email.analysis.priority_score} />
              <CategoryBadge name={email.analysis.category_name} />
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="btn-ghost flex items-center gap-1.5 text-xs"
            title="Re-run AI analysis"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${reanalyzing ? 'animate-spin' : ''}`} />
            {reanalyzing ? 'Analyzing...' : 'Re-analyze'}
          </button>
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="btn-ghost flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Delete
          </button>
        </div>
      </div>

      {/* Main two-column layout */}
      <div className="grid grid-cols-1 xl:grid-cols-5 gap-0 xl:gap-6 p-6">
        {/* LEFT: Email content */}
        <div className="xl:col-span-3 space-y-4">
          {/* Email header */}
          <div className="card">
            <h1 className="text-xl font-bold text-white mb-4 leading-snug">
              {email.subject || '(No Subject)'}
            </h1>
            <div className="space-y-2 text-sm pb-4 border-b border-slate-700">
              <div className="flex items-center gap-2">
                <User className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-slate-300 font-medium">
                  {email.sender_name || 'Unknown Sender'}
                </span>
              </div>
              {email.sender_email && (
                <div className="flex items-center gap-2">
                  <AtSign className="w-3.5 h-3.5 text-slate-500" />
                  <span className="text-slate-400">{email.sender_email}</span>
                </div>
              )}
              <div className="flex items-center gap-2">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-slate-400">{formatDateTime(email.received_at)}</span>
              </div>
            </div>

            {/* Email body */}
            <div className="pt-4">
              <pre className="text-sm text-slate-200 whitespace-pre-wrap font-sans leading-7">
                {email.body}
              </pre>
            </div>
          </div>

          {/* Reply editor */}
          <ReplyEditor
            emailId={email.id}
            reply={email.reply}
            onReplyUpdate={handleReplyUpdate}
          />
        </div>

        {/* RIGHT: AI analysis panel */}
        <div className="xl:col-span-2 space-y-0 mt-4 xl:mt-0">
          {email.is_analyzed && email.analysis ? (
            <AIInsightPanel
              analysis={email.analysis}
              entities={email.entities ?? []}
            />
          ) : (
            <div className="card text-center py-10">
              <div className="w-12 h-12 rounded-full bg-blue-600/20 flex items-center justify-center mx-auto mb-3">
                <RefreshCw className="w-6 h-6 text-blue-400 animate-spin" />
              </div>
              <p className="text-sm text-slate-400">AI analysis in progress...</p>
              <button onClick={load} className="btn-secondary text-xs mt-4">
                Refresh
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function DetailSkeleton() {
  return (
    <div className="p-6 space-y-4">
      <div className="h-8 w-24 bg-slate-800 rounded animate-pulse" />
      <div className="grid grid-cols-5 gap-6">
        <div className="col-span-3 space-y-4">
          <div className="card space-y-3">
            <div className="h-6 bg-slate-700 rounded w-3/4 animate-pulse" />
            <div className="h-4 bg-slate-700 rounded w-1/3 animate-pulse" />
            <div className="h-32 bg-slate-700 rounded animate-pulse" />
          </div>
        </div>
        <div className="col-span-2 space-y-4">
          <div className="card h-64 animate-pulse" />
          <div className="card h-48 animate-pulse" />
        </div>
      </div>
    </div>
  )
}
