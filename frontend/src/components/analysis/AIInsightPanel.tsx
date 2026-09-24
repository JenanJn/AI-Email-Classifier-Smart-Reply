import { ShieldCheck, Zap, Target, Clock, Brain, TrendingUp } from 'lucide-react'
import clsx from 'clsx'
import type { Analysis, Entity } from '../../types'
import PriorityBadge from '../email/PriorityBadge'
import CategoryBadge from '../email/CategoryBadge'
import ConfidenceMeter from './ConfidenceMeter'
import PriorityScoreRing from './PriorityScoreRing'
import EntityList from './EntityList'
import { getCategoryColor } from '../../utils/categoryUtils'

interface Props {
  analysis: Analysis
  entities: Entity[]
}

export default function AIInsightPanel({ analysis, entities }: Props) {
  const catColor = getCategoryColor(analysis.category_name)

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Classification card */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-bold text-blue-400 uppercase tracking-wider">AI Classification</span>
        </div>

        <div className="flex items-start justify-between gap-4">
          <div className="space-y-3 flex-1">
            {/* Category */}
            <div>
              <p className="label">Category</p>
              <CategoryBadge name={analysis.category_name} />
            </div>
            {/* Intent */}
            <div>
              <p className="label">Intent</p>
              <p className="text-sm text-white font-medium">{analysis.intent ?? '—'}</p>
            </div>
            {/* Sentiment */}
            {analysis.sentiment && (
              <div>
                <p className="label">Sentiment</p>
                <span className={clsx(
                  'text-xs font-semibold capitalize px-2 py-0.5 rounded-full',
                  analysis.sentiment === 'positive' && 'bg-emerald-500/20 text-emerald-300',
                  analysis.sentiment === 'negative' && 'bg-red-500/20 text-red-300',
                  analysis.sentiment === 'neutral' && 'bg-slate-700 text-slate-400',
                )}>
                  {analysis.sentiment}
                </span>
              </div>
            )}
          </div>

          {/* Confidence ring */}
          <ConfidenceMeter
            value={analysis.category_confidence ?? 0}
            label="Confidence"
            color={catColor}
          />
        </div>
      </div>

      {/* Priority card */}
      <div className="card">
        <div className="flex items-center gap-2 mb-4">
          <TrendingUp className="w-4 h-4 text-amber-400" />
          <span className="text-xs font-bold text-amber-400 uppercase tracking-wider">Priority Analysis</span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <div className="space-y-3">
            <div>
              <p className="label">Priority Level</p>
              <PriorityBadge level={analysis.priority_level} size="md" />
            </div>
            <div>
              <p className="label">Urgency</p>
              <p className="text-sm text-white capitalize">{analysis.urgency_level ?? '—'}</p>
            </div>
            <div>
              <p className="label">Action Required</p>
              <span className={clsx(
                'text-xs font-bold px-2 py-0.5 rounded-full',
                analysis.action_required
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                  : 'bg-slate-700 text-slate-400',
              )}>
                {analysis.action_required ? '✓ Yes' : '✗ No'}
              </span>
            </div>
            {analysis.deadline_text && (
              <div>
                <p className="label">Deadline / Date</p>
                <div className="flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <p className="text-sm text-amber-300 font-medium">{analysis.deadline_text}</p>
                </div>
              </div>
            )}
          </div>

          <PriorityScoreRing
            score={analysis.priority_score ?? 0}
            level={analysis.priority_level}
          />
        </div>
      </div>

      {/* Why this priority */}
      {analysis.ai_explanation && analysis.ai_explanation.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <ShieldCheck className="w-4 h-4 text-purple-400" />
            <span className="text-xs font-bold text-purple-400 uppercase tracking-wider">
              Why This Priority?
            </span>
          </div>
          <ul className="space-y-2">
            {analysis.ai_explanation.map((reason, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-purple-400 flex-shrink-0" />
                <span className="text-sm text-slate-300">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Key points */}
      {analysis.key_points && analysis.key_points.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Target className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Key Points</span>
          </div>
          <ul className="space-y-2">
            {analysis.key_points.map((point, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-cyan-400 flex-shrink-0" />
                <span className="text-sm text-slate-300">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Entities */}
      {entities.length > 0 && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-xs font-bold text-yellow-400 uppercase tracking-wider">
              Detected Information
            </span>
          </div>
          <EntityList entities={entities} />
        </div>
      )}
    </div>
  )
}
