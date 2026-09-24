import apiClient from './client'
import type { Reply, ReplyVersion } from '../types'

export const repliesApi = {
  generate: (emailId: string) =>
    apiClient.post<Reply>(`/emails/${emailId}/reply/generate`).then((r) => r.data),

  regenerate: (emailId: string) =>
    apiClient.post<Reply>(`/emails/${emailId}/reply/regenerate`).then((r) => r.data),

  modify: (emailId: string, style: 'shorter' | 'formal' | 'friendly' | 'longer') =>
    apiClient.post<Reply>(`/emails/${emailId}/reply/modify`, { style }).then((r) => r.data),

  edit: (emailId: string, content: string, status?: string) =>
    apiClient.patch<Reply>(`/emails/${emailId}/reply`, { content, status }).then((r) => r.data),

  history: (emailId: string) =>
    apiClient.get<ReplyVersion[]>(`/emails/${emailId}/reply/history`).then((r) => r.data),
}
