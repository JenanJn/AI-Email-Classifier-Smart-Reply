export type PriorityLevel = 'high' | 'medium' | 'low' | null

export function getPriorityColor(level: PriorityLevel): string {
  switch (level) {
    case 'high': return 'text-red-400'
    case 'medium': return 'text-amber-400'
    case 'low': return 'text-emerald-400'
    default: return 'text-slate-400'
  }
}

export function getPriorityBgColor(level: PriorityLevel): string {
  switch (level) {
    case 'high': return 'bg-red-500/20 text-red-300 border border-red-500/30'
    case 'medium': return 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
    case 'low': return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
    default: return 'bg-slate-700 text-slate-400'
  }
}

export function getPriorityDot(level: PriorityLevel): string {
  switch (level) {
    case 'high': return 'bg-red-500'
    case 'medium': return 'bg-amber-500'
    case 'low': return 'bg-emerald-500'
    default: return 'bg-slate-500'
  }
}

export function getPriorityBarColor(level: PriorityLevel): string {
  switch (level) {
    case 'high': return '#EF4444'
    case 'medium': return '#F59E0B'
    case 'low': return '#10B981'
    default: return '#64748B'
  }
}

export function getPriorityLabel(level: PriorityLevel): string {
  switch (level) {
    case 'high': return 'HIGH'
    case 'medium': return 'MEDIUM'
    case 'low': return 'LOW'
    default: return 'UNKNOWN'
  }
}
