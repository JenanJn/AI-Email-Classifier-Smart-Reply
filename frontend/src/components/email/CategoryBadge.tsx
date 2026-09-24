import { getCategoryBadgeStyle, getCategoryIcon } from '../../utils/categoryUtils'

interface Props {
  name: string | null
  showIcon?: boolean
}

export default function CategoryBadge({ name, showIcon = true }: Props) {
  return (
    <span
      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold"
      style={getCategoryBadgeStyle(name)}
    >
      {showIcon && <span>{getCategoryIcon(name)}</span>}
      {name ?? 'Uncategorized'}
    </span>
  )
}
