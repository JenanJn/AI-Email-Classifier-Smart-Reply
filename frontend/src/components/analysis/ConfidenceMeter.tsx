interface Props {
  value: number  // 0–1
  label?: string
  color?: string
}

export default function ConfidenceMeter({ value, label, color = '#3B82F6' }: Props) {
  const pct = Math.round(value * 100)
  const circumference = 2 * Math.PI * 28

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative w-16 h-16">
        <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
          <circle
            cx="32" cy="32" r="28"
            fill="none" stroke="#1E293B" strokeWidth="5"
          />
          <circle
            cx="32" cy="32" r="28"
            fill="none"
            stroke={color}
            strokeWidth="5"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * (1 - value)}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 0.6s ease' }}
          />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-white">
          {pct}%
        </span>
      </div>
      {label && <p className="text-xs text-slate-400 text-center">{label}</p>}
    </div>
  )
}
