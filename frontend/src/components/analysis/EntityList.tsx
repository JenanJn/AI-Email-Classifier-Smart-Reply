import type { Entity } from '../../types'

const ENTITY_STYLE: Record<string, { label: string; bg: string; text: string }> = {
  PERSON:   { label: 'Person',       bg: 'bg-blue-500/15',    text: 'text-blue-300' },
  ORG:      { label: 'Organization', bg: 'bg-purple-500/15',  text: 'text-purple-300' },
  DATE:     { label: 'Date',         bg: 'bg-amber-500/15',   text: 'text-amber-300' },
  TIME:     { label: 'Time',         bg: 'bg-orange-500/15',  text: 'text-orange-300' },
  MONEY:    { label: 'Amount',       bg: 'bg-emerald-500/15', text: 'text-emerald-300' },
  GPE:      { label: 'Location',     bg: 'bg-cyan-500/15',    text: 'text-cyan-300' },
  EVENT:    { label: 'Event',        bg: 'bg-pink-500/15',    text: 'text-pink-300' },
  CARDINAL: { label: 'Number',       bg: 'bg-slate-600/50',   text: 'text-slate-300' },
  ORDINAL:  { label: 'Order',        bg: 'bg-slate-600/50',   text: 'text-slate-300' },
}

interface Props {
  entities: Entity[]
}

export default function EntityList({ entities }: Props) {
  if (!entities.length) return null

  return (
    <div className="flex flex-wrap gap-2">
      {entities.map((e) => {
        const style = ENTITY_STYLE[e.entity_type] ?? {
          label: e.entity_type,
          bg: 'bg-slate-700',
          text: 'text-slate-300',
        }
        return (
          <div
            key={e.id}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg ${style.bg}`}
            title={style.label}
          >
            <span className={`text-[10px] font-bold uppercase tracking-wider opacity-60 ${style.text}`}>
              {style.label}
            </span>
            <span className={`text-xs font-semibold ${style.text}`}>{e.entity_text}</span>
          </div>
        )
      })}
    </div>
  )
}
