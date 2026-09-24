import { useNavigate } from 'react-router-dom'
import { Clock, Zap } from 'lucide-react'
import clsx from 'clsx'
import type { EmailListItem } from '../../types'
import PriorityBadge from './PriorityBadge'
import CategoryBadge from './CategoryBadge'
import { timeAgo } from '../../utils/dateFormat'
import { getPriorityDot } from '../../utils/priorityUtils'

interface Props {
  email: EmailListItem
}

export default function EmailCard({ email }: Props) {
  const navigate = useNavigate()

  return (
    <div
      onClick={() => navigate(`/inbox/${email.id}`)}
      className={clsx(
        'group flex gap-4 px-5 py-4 border-b border-slate-800 hover:bg-slate-800/60 cursor-pointer transition-colors duration-150',
        email.priority_level === 'high' && 'border-l-2 border-l-red-500',
        email.priority_level === 'medium' && 'border-l-2 border-l-amber-500',
        email.priority_level === 'low' && 'border-l-2 border-l-emerald-500',
      )}
    >
      {/* Priority dot */}
      <div className="flex-shrink-0 pt-1">
        <span className={clsx('block w-2 h-2 rounded-full mt-1', getPriorityDot(email.priority_level))} />
      </div>

      {/* Main content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2 mb-1">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-white truncate">
              {email.sender_name || email.sender_email || 'Unknown Sender'}
            </p>
            <p className="text-sm text-slate-300 truncate mt-0.5">
              {email.subject || '(No subject)'}
            </p>
          </div>
          <span className="flex-shrink-0 text-xs text-slate-500 whitespace-nowrap">
            {timeAgo(email.received_at)}
          </span>
        </div>

        <div className="flex items-center gap-2 flex-wrap mt-2">
          {email.is_analyzed && (
            <>
              <PriorityBadge level={email.priority_level} score={email.priority_score} />
              <CategoryBadge name={email.category_name} />
              {email.intent && (
                <span className="text-xs text-slate-500">{email.intent}</span>
              )}
              {email.action_required && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30">
                  <Zap className="w-2.5 h-2.5" /> Action Required
                </span>
              )}
            </>
          )}
          {!email.is_analyzed && (
            <span className="text-xs text-slate-500 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Analyzing...
            </span>
          )}
        </div>
      </div>
    </div>
  )
}
