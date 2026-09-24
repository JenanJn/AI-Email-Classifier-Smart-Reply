import clsx from 'clsx'
import type { PriorityLevel } from '../../utils/priorityUtils'
import { getPriorityBgColor, getPriorityLabel } from '../../utils/priorityUtils'

interface Props {
  level: PriorityLevel
  score?: number | null
  size?: 'sm' | 'md'
}

export default function PriorityBadge({ level, score, size = 'sm' }: Props) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full font-bold',
        getPriorityBgColor(level),
        size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm',
      )}
    >
      <span
        className={clsx(
          'rounded-full',
          size === 'sm' ? 'w-1.5 h-1.5' : 'w-2 h-2',
          level === 'high' ? 'bg-red-400' : level === 'medium' ? 'bg-amber-400' : 'bg-emerald-400',
        )}
      />
      {getPriorityLabel(level)}
      {score != null && <span className="opacity-75">· {score}</span>}
    </span>
  )
}
