import apiClient from './client'
import type { AnalyticsInsights, AnalyticsSummary, AnalyticsTrends } from '../types'

export const analyticsApi = {
  summary: () =>
    apiClient.get<AnalyticsSummary>('/analytics/summary').then((r) => r.data),

  trends: (period = 30) =>
    apiClient.get<AnalyticsTrends>('/analytics/trends', { params: { period } }).then((r) => r.data),

  insights: () =>
    apiClient.get<AnalyticsInsights>('/analytics/insights').then((r) => r.data),
}
