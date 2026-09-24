export interface User {
  id: string
  name: string
  email: string
}

export interface AuthState {
  user: User | null
  token: string | null
}

export interface Entity {
  id: string
  entity_type: string
  entity_text: string
  confidence: number | null
}

export interface Analysis {
  id: string
  category_name: string | null
  category_confidence: number | null
  intent: string | null
  priority_level: 'low' | 'medium' | 'high' | null
  priority_score: number | null
  urgency_level: string | null
  sentiment: string | null
  sentiment_score: number | null
  action_required: boolean
  deadline_text: string | null
  key_points: string[] | null
  ai_explanation: string[] | null
  priority_factors: string | null
  analyzed_at: string | null
}

export interface Reply {
  id: string
  current_content: string
  tone: string
  status: string
  is_user_edited: boolean
  generated_at: string
  updated_at: string
  versions?: ReplyVersion[]
}

export interface ReplyVersion {
  id: string
  version_num: number
  content: string
  change_type: string
  created_at: string
}

export interface Email {
  id: string
  sender_name: string | null
  sender_email: string | null
  subject: string | null
  body: string
  received_at: string
  is_analyzed: boolean
  created_at: string
  analysis: Analysis | null
  entities: Entity[] | null
  reply: Reply | null
}

export interface EmailListItem {
  id: string
  sender_name: string | null
  sender_email: string | null
  subject: string | null
  received_at: string
  is_analyzed: boolean
  category_name: string | null
  priority_level: 'low' | 'medium' | 'high' | null
  priority_score: number | null
  action_required: boolean | null
  intent: string | null
}

export interface PaginatedEmails {
  items: EmailListItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AnalyticsSummary {
  total_emails: number
  high_priority: number
  medium_priority: number
  low_priority: number
  action_required: number
  analyzed: number
  replies_generated: number
  avg_priority_score: number
  action_required_percentage: number
}

export interface CategoryCount {
  category: string
  count: number
  percentage: number
}

export interface PriorityCount {
  level: string
  count: number
  percentage: number
}

export interface DailyVolume {
  date: string
  count: number
}

export interface CategoryPriorityAvg {
  category: string
  avg_priority: number
}

export interface AnalyticsTrends {
  daily_volume: DailyVolume[]
  category_distribution: CategoryCount[]
  priority_distribution: PriorityCount[]
  avg_priority_by_category: CategoryPriorityAvg[]
}

export interface AIInsight {
  insight: string
  type: 'info' | 'warning' | 'tip'
}

export interface AnalyticsInsights {
  insights: AIInsight[]
}

export interface Category {
  id: number
  name: string
  slug: string
  icon: string
  color: string
}
