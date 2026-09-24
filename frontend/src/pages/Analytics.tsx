import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  BarChart3, TrendingUp, Mail, Zap, Brain,
  AlertTriangle, Info, Lightbulb, RefreshCw,
} from 'lucide-react'
import { analyticsApi } from '../api/analytics'
import type { AnalyticsSummary, AnalyticsTrends, AIInsight } from '../types'

const CHART_COLORS = [
  '#6366F1', '#3B82F6', '#F59E0B', '#EF4444', '#10B981',
  '#06B6D4', '#EC4899', '#F97316', '#8B5CF6', '#64748B',
  '#A855F7', '#0EA5E9', '#14B8A6', '#94A3B8',
]

const TOOLTIP_STYLE = {
  contentStyle: {
    background: '#1E293B',
    border: '1px solid #334155',
    borderRadius: 8,
    fontSize: 12,
    color: '#F8FAFC',
  },
  labelStyle: { color: '#94A3B8' },
}

export default function Analytics() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [trends, setTrends] = useState<AnalyticsTrends | null>(null)
  const [insights, setInsights] = useState<AIInsight[]>([])
  const [period, setPeriod] = useState(30)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      const [sum, trend, ins] = await Promise.all([
        analyticsApi.summary(),
        analyticsApi.trends(period),
        analyticsApi.insights(),
      ])
      setSummary(sum)
      setTrends(trend)
      setInsights(ins.insights)
    } catch {
      // silently handle
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [period])

  return (
    <div className="p-6 space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-400" />
            Email Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-0.5">Patterns and trends from your inbox</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="input text-sm py-1.5 w-36"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
          <button onClick={load} className="btn-ghost flex items-center gap-1.5 text-xs">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {loading ? (
        <AnalyticsSkeleton />
      ) : (
        <>
          {/* Summary stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard label="Total Emails" value={summary?.total_emails ?? 0} icon={<Mail className="w-4 h-4 text-blue-400" />} />
            <MetricCard label="Replies Generated" value={summary?.replies_generated ?? 0} icon={<Brain className="w-4 h-4 text-purple-400" />} />
            <MetricCard label="Action Required" value={`${summary?.action_required_percentage ?? 0}%`} icon={<Zap className="w-4 h-4 text-amber-400" />} />
            <MetricCard label="Avg Priority Score" value={`${summary?.avg_priority_score ?? 0}/100`} icon={<TrendingUp className="w-4 h-4 text-emerald-400" />} />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Volume over time */}
            {trends?.daily_volume && trends.daily_volume.length > 0 && (
              <div className="card lg:col-span-2">
                <h2 className="text-sm font-bold text-white mb-4">Email Volume Over Time</h2>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={trends.daily_volume}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis
                      dataKey="date"
                      tick={{ fontSize: 11, fill: '#64748B' }}
                      tickFormatter={(d) => d.slice(5)}
                    />
                    <YAxis tick={{ fontSize: 11, fill: '#64748B' }} allowDecimals={false} />
                    <Tooltip {...TOOLTIP_STYLE} />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#3B82F6"
                      strokeWidth={2}
                      dot={{ fill: '#3B82F6', r: 3 }}
                      name="Emails"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Category distribution */}
            {trends?.category_distribution && trends.category_distribution.length > 0 && (
              <div className="card">
                <h2 className="text-sm font-bold text-white mb-4">Emails by Category</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={trends.category_distribution.slice(0, 8)}
                    layout="vertical"
                    margin={{ left: 8, right: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11, fill: '#64748B' }} allowDecimals={false} />
                    <YAxis
                      dataKey="category"
                      type="category"
                      tick={{ fontSize: 10, fill: '#94A3B8' }}
                      width={130}
                      tickFormatter={(v) => v.length > 18 ? v.slice(0, 18) + '…' : v}
                    />
                    <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [`${v} emails`]} />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {trends.category_distribution.slice(0, 8).map((_, i) => (
                        <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Average priority by category */}
            {trends?.avg_priority_by_category && trends.avg_priority_by_category.length > 0 && (
              <div className="card">
                <h2 className="text-sm font-bold text-white mb-4">Average Priority Score by Category</h2>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart
                    data={trends.avg_priority_by_category.slice(0, 8)}
                    layout="vertical"
                    margin={{ left: 8, right: 20 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748B' }} />
                    <YAxis
                      dataKey="category"
                      type="category"
                      tick={{ fontSize: 10, fill: '#94A3B8' }}
                      width={130}
                      tickFormatter={(v) => v.length > 18 ? v.slice(0, 18) + '…' : v}
                    />
                    <Tooltip {...TOOLTIP_STYLE} formatter={(v) => [`${v}/100`]} />
                    <Bar dataKey="avg_priority" name="Avg Score" radius={[0, 4, 4, 0]}>
                      {trends.avg_priority_by_category.slice(0, 8).map((item, i) => {
                        const color = item.avg_priority >= 70 ? '#EF4444'
                          : item.avg_priority >= 40 ? '#F59E0B' : '#10B981'
                        return <Cell key={i} fill={color} />
                      })}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Priority + AI Insights row */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Priority distribution */}
            {trends?.priority_distribution && trends.priority_distribution.length > 0 && (
              <div className="card">
                <h2 className="text-sm font-bold text-white mb-4">Priority Distribution</h2>
                <div className="flex items-center gap-6">
                  <ResponsiveContainer width="50%" height={160}>
                    <PieChart>
                      <Pie
                        data={trends.priority_distribution}
                        cx="50%" cy="50%"
                        innerRadius={45} outerRadius={70}
                        dataKey="count" nameKey="level"
                        paddingAngle={3}
                      >
                        {trends.priority_distribution.map((item) => {
                          const color = item.level === 'high' ? '#EF4444'
                            : item.level === 'medium' ? '#F59E0B' : '#10B981'
                          return <Cell key={item.level} fill={color} />
                        })}
                      </Pie>
                      <Tooltip {...TOOLTIP_STYLE} />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="space-y-3 flex-1">
                    {['high', 'medium', 'low'].map((level) => {
                      const item = trends.priority_distribution.find((p) => p.level === level)
                      if (!item) return null
                      const color = level === 'high' ? '#EF4444' : level === 'medium' ? '#F59E0B' : '#10B981'
                      return (
                        <div key={level}>
                          <div className="flex justify-between text-xs mb-1">
                            <span className="capitalize text-slate-300 font-medium">{level}</span>
                            <span className="text-slate-400">{item.percentage}%</span>
                          </div>
                          <div className="h-1.5 rounded-full bg-slate-700">
                            <div className="h-1.5 rounded-full" style={{ width: `${item.percentage}%`, background: color }} />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            )}

            {/* AI Insights */}
            {insights.length > 0 && (
              <div className="card">
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb className="w-4 h-4 text-yellow-400" />
                  <h2 className="text-sm font-bold text-white">AI Insights</h2>
                </div>
                <div className="space-y-2">
                  {insights.map((insight, i) => {
                    const Icon = insight.type === 'warning' ? AlertTriangle : insight.type === 'tip' ? Lightbulb : Info
                    const style =
                      insight.type === 'warning'
                        ? 'bg-amber-500/10 border-amber-500/20 text-amber-300'
                        : insight.type === 'tip'
                        ? 'bg-blue-500/10 border-blue-500/20 text-blue-300'
                        : 'bg-slate-700/50 border-slate-700 text-slate-300'
                    return (
                      <div key={i} className={`flex items-start gap-2.5 px-3 py-2.5 rounded-lg border ${style}`}>
                        <Icon className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
                        <p className="text-xs leading-relaxed">{insight.insight}</p>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}

function MetricCard({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <div className="card flex items-center gap-3">
      <div className="w-9 h-9 rounded-lg bg-slate-700 flex items-center justify-center flex-shrink-0">{icon}</div>
      <div>
        <p className="text-xs text-slate-400">{label}</p>
        <p className="text-xl font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

function AnalyticsSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => <div key={i} className="h-20 bg-slate-800 rounded-xl animate-pulse" />)}
      </div>
      <div className="h-52 bg-slate-800 rounded-xl animate-pulse" />
      <div className="grid grid-cols-2 gap-6">
        <div className="h-80 bg-slate-800 rounded-xl animate-pulse" />
        <div className="h-80 bg-slate-800 rounded-xl animate-pulse" />
      </div>
    </div>
  )
}

import type React from 'react'
