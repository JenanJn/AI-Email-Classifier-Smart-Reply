// Category metadata for display
export const CATEGORY_META: Record<string, { icon: string; color: string }> = {
  'Job / Career':           { icon: '💼', color: '#6366F1' },
  'Work / Professional':    { icon: '🏢', color: '#8B5CF6' },
  'Education':              { icon: '🎓', color: '#3B82F6' },
  'E-commerce / Shopping':  { icon: '🛍️', color: '#F59E0B' },
  'Finance / Banking':      { icon: '💳', color: '#EF4444' },
  'Travel':                 { icon: '✈️', color: '#06B6D4' },
  'Healthcare':             { icon: '🏥', color: '#EC4899' },
  'Social / Personal':      { icon: '👥', color: '#10B981' },
  'Events / Invitations':   { icon: '📅', color: '#F97316' },
  'Government / Official':  { icon: '🏛️', color: '#64748B' },
  'Promotions / Marketing': { icon: '🏷️', color: '#A855F7' },
  'Notifications':          { icon: '🔔', color: '#0EA5E9' },
  'Customer Support':       { icon: '🎧', color: '#14B8A6' },
  'Other':                  { icon: '📧', color: '#94A3B8' },
}

export function getCategoryIcon(name: string | null): string {
  if (!name) return '📧'
  return CATEGORY_META[name]?.icon ?? '📧'
}

export function getCategoryColor(name: string | null): string {
  if (!name) return '#94A3B8'
  return CATEGORY_META[name]?.color ?? '#94A3B8'
}

export function getCategoryBadgeStyle(name: string | null): React.CSSProperties {
  const color = getCategoryColor(name)
  return {
    backgroundColor: `${color}20`,
    color: color,
    border: `1px solid ${color}40`,
  }
}

// Need React for CSSProperties
import type React from 'react'
