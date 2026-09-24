import { getPriorityBarColor } from '../../utils/priorityUtils'
import type { PriorityLevel } from '../../utils/priorityUtils'

interface Props {
  score: number
  level: PriorityLevel
}

export default function PriorityScoreRing({ score, level }: Props) {
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const progress = score / 100
  const color = getPriorityBarColor(level)

  return (
    <div className="relative w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r={radius} fill="none" stroke="#1E293B" strokeWidth="6" />
        <circle
          cx="44" cy="44" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={circumference * (1 - progress)}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-black text-white">{score}</span>
        <span className="text-xs text-slate-400 font-medium">/100</span>
      </div>
    </div>
  )
}
