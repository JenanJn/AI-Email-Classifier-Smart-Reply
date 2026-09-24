import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Mail, Flame, Zap, Clock, TrendingUp, Brain,
  AlertTriangle, Info, Lightbulb, ArrowRight, RefreshCw,
} from 'lucide-react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from 'recharts'
import clsx from 'clsx'
import { analyticsApi } from '../api/analytics'
import { emailsApi } from '../api/emails'
import type { AnalyticsSummary, AnalyticsTrends, AIInsight, EmailListItem } from '../types'
import PriorityBadge from '../components/email/PriorityBadge'
import CategoryBadge from '../components/email/CategoryBadge'
import { timeAgo } from '../utils/dateFormat'
import { getPriorityBgColor } from '../utils/priorityUtils'

// Colour palette for category pie chart
const CHART_COLORS = [
  '#6366F1', '#3B82F6', '#F59E0B', '#EF4444', '#10B981',
  '#06B6D4', '#EC4899', '#F97316', '#8B5CF6', '#64748B',
  '#A855F7', '#0EA5E9', '#14B8A6', '#94A3B8',
]

export default function Dashboard() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [trends, setTrends] = useState<AnalyticsTrends | null>(null)
  const [insights, setInsights] = useState<AIInsight[]>([])
  const [actionQueue, setActionQueue] = useState<EmailListItem[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [sum, trend, ins, emails] = await Promise.all([
        analyticsApi.summary(),
        analyticsApi.trends(30),
        analyticsApi.insights(),
        emailsApi.list({ action_required: true, page_size: 5, page: 1 }),
      ])
      setSummary(sum)
      setTrends(trend)
      setInsights(ins.insights)
      setActionQueue(emails.items)
    } catch {
      // silently handle
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <LoadingSkeleton />

  const PRIORITY_COLORS: Record<string, string> = { high: '#EF4444', medium: '#F59E0B', low: '#10B981' }

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Brain className="w-6 h-6 text-blue-400" />
            AI Command Center
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">Your intelligent inbox overview</p>
        </div>
        <button onClick={load} className="btn-ghost flex items-center gap-1.5 text-xs">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh
        </button>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Mail className="w-5 h-5 text-blue-400" />}
          label="Total Emails"
          value={summary?.total_emails ?? 0}
          sub={`${summary?.analyzed ?? 0} analyzed`}
          color="blue"
        />
        <StatCard
          icon={<Flame className="w-5 h-5 text-red-400" />}
          label="High Priority"
          value={summary?.high_priority ?? 0}
          sub={`${summary?.medium_priority ?? 0} medium`}
          color="red"
        />
        <StatCard
          icon={<Zap className="w-5 h-5 text-amber-400" />}
          label="Action Required"
          value={summary?.action_required ?? 0}
          sub={`${summary?.action_required_percentage ?? 0}% of inbox`}
          color="amber"
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5 text-emerald-400" />}
          label="Avg Priority"
          value={summary?.avg_priority_score ?? 0}
          sub="out of 100"
          color="emerald"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Action Queue — takes 2 cols */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-amber-400" />
                <h2 className="text-sm font-bold text-white">AI Action Queue</h2>
                <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300">
                  {actionQueue.length} pending
                </span>
              </div>
              <button
                onClick={() => navigate('/inbox?action_required=true')}
                className="btn-ghost text-xs flex items-center gap-1"
              >
                View all <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {actionQueue.length === 0 ? (
              <div className="text-center py-8 text-slate-500 text-sm">
                No emails requiring action right now.
              </div>
            ) : (
              <div className="space-y-2">
                {actionQueue.map((email) => (
                  <ActionQueueItem
                    key={email.id}
                    email={email}
                    onClick={() => navigate(`/inbox/${email.id}`)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* AI Insights */}
          {insights.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <Lightbulb className="w-4 h-4 text-yellow-400" />
                <h2 className="text-sm font-bold text-white">AI Insights</h2>
              </div>
              <div className="space-y-2">
                {insights.map((insight, i) => (
                  <InsightItem key={i} insight={insight} />
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Charts column */}
        <div className="space-y-4">
          {/* Category distribution */}
          {trends?.category_distribution && trends.category_distribution.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-bold text-white mb-4">Email Categories</h2>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie
                    data={trends.category_distribution.slice(0, 8)}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={72}
                    dataKey="count"
                    nameKey="category"
                    paddingAngle={2}
                  >
                    {trends.category_distribution.slice(0, 8).map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
                    formatter={(value: number, name: string) => [`${value} emails`, name]}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 mt-2">
                {trends.category_distribution.slice(0, 5).map((cat, i) => (
                  <div key={cat.category} className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: CHART_COLORS[i] }} />
                    <span className="text-slate-400 truncate flex-1">{cat.category}</span>
                    <span className="text-slate-300 font-medium">{cat.count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Priority breakdown */}
          {trends?.priority_distribution && trends.priority_distribution.length > 0 && (
            <div className="card">
              <h2 className="text-sm font-bold text-white mb-4">Priority Split</h2>
              <div className="space-y-3">
                {['high', 'medium', 'low'].map((level) => {
                  const item = trends.priority_distribution.find((p) => p.level === level)
                  if (!item) return null
                  return (
                    <div key={level}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="capitalize font-medium text-slate-300">{level}</span>
                        <span className="text-slate-400">{item.count} ({item.percentage}%)</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-slate-700">
                        <div
                          className="h-1.5 rounded-full transition-all duration-500"
                          style={{
                            width: `${item.percentage}%`,
                            background: PRIORITY_COLORS[level],
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Sub-components ────────────────────────────────────────────────────────────

function StatCard({
  icon, label, value, sub, color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  sub: string
  color: 'blue' | 'red' | 'amber' | 'emerald'
}) {
  const bgMap = {
    blue: 'bg-blue-500/10 border-blue-500/20',
    red: 'bg-red-500/10 border-red-500/20',
    amber: 'bg-amber-500/10 border-amber-500/20',
    emerald: 'bg-emerald-500/10 border-emerald-500/20',
  }
  return (
    <div className={`rounded-xl p-4 border ${bgMap[color]}`}>
      <div className="flex items-center gap-2 mb-3">{icon}<span className="text-xs text-slate-400 font-medium">{label}</span></div>
      <p className="text-3xl font-black text-white">{value}</p>
      <p className="text-xs text-slate-500 mt-1">{sub}</p>
    </div>
  )
}

function ActionQueueItem({ email, onClick }: { email: EmailListItem; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors duration-150 border',
        email.priority_level === 'high'
          ? 'bg-red-500/5 border-red-500/20 hover:bg-red-500/10'
          : email.priority_level === 'medium'
          ? 'bg-amber-500/5 border-amber-500/20 hover:bg-amber-500/10'
          : 'bg-slate-700/40 border-slate-700 hover:bg-slate-700/70',
      )}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <PriorityBadge level={email.priority_level} score={email.priority_score} />
          <CategoryBadge name={email.category_name} />
        </div>
        <p className="text-sm font-semibold text-white truncate">
          {email.subject || '(No subject)'}
        </p>
        <p className="text-xs text-slate-400 truncate mt-0.5">
          {email.sender_name || email.sender_email} · {timeAgo(email.received_at)}
        </p>
        {email.intent && (
          <p className="text-xs text-slate-500 mt-0.5">{email.intent}</p>
        )}
      </div>
      <ArrowRight className="w-4 h-4 text-slate-500 flex-shrink-0 mt-1" />
    </div>
  )
}

function InsightItem({ insight }: { insight: AIInsight }) {
  const Icon = insight.type === 'warning' ? AlertTriangle : insight.type === 'tip' ? Lightbulb : Info
  const style =
    insight.type === 'warning'
      ? 'bg-amber-500/10 border-amber-500/20 text-amber-300'
      : insight.type === 'tip'
      ? 'bg-blue-500/10 border-blue-500/20 text-blue-300'
      : 'bg-slate-700/50 border-slate-700 text-slate-300'

  return (
    <div className={`flex items-start gap-2.5 px-3 py-2.5 rounded-lg border ${style}`}>
      <Icon className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
      <p className="text-xs leading-relaxed">{insight.insight}</p>
    </div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="p-6 space-y-6">
      <div className="h-8 w-48 bg-slate-800 rounded-lg animate-pulse" />
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-28 bg-slate-800 rounded-xl animate-pulse" />
        ))}
      </div>
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 h-64 bg-slate-800 rounded-xl animate-pulse" />
        <div className="h-64 bg-slate-800 rounded-xl animate-pulse" />
      </div>
    </div>
  )
}

import type React from 'react'
