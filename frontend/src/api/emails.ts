import apiClient from './client'
import type { Email, EmailListItem, PaginatedEmails } from '../types'

export interface EmailCreatePayload {
  sender_name?: string
  sender_email?: string
  subject?: string
  body: string
  received_at?: string
}

export interface EmailListParams {
  page?: number
  page_size?: number
  category?: string
  priority?: string
  action_required?: boolean
  search?: string
}

export const emailsApi = {
  create: (payload: EmailCreatePayload) =>
    apiClient.post<Email>('/emails', payload).then((r) => r.data),

  list: (params: EmailListParams = {}) =>
    apiClient.get<PaginatedEmails>('/emails', { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Email>(`/emails/${id}`).then((r) => r.data),

  analyze: (id: string) =>
    apiClient.post<Email>(`/emails/${id}/analyze`).then((r) => r.data),

  delete: (id: string) =>
    apiClient.delete(`/emails/${id}`),
}
