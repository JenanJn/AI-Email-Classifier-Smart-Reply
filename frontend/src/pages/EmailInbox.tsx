import { useEffect, useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Search, SlidersHorizontal, X, ChevronLeft, ChevronRight, Inbox } from 'lucide-react'
import { emailsApi } from '../api/emails'
import type { EmailListItem, PaginatedEmails } from '../types'
import EmailCard from '../components/email/EmailCard'
import clsx from 'clsx'

const PRIORITIES = ['', 'high', 'medium', 'low']
const CATEGORIES = [
  '', 'Job / Career', 'Work / Professional', 'Education',
  'E-commerce / Shopping', 'Finance / Banking', 'Travel', 'Healthcare',
  'Social / Personal', 'Events / Invitations', 'Government / Official',
  'Promotions / Marketing', 'Notifications', 'Customer Support', 'Other',
]

export default function EmailInbox() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [emails, setEmails] = useState<EmailListItem[]>([])
  const [pagination, setPagination] = useState({ total: 0, page: 1, totalPages: 1 })
  const [loading, setLoading] = useState(true)

  // Filters from URL params
  const search = searchParams.get('search') ?? ''
  const priority = searchParams.get('priority') ?? ''
  const category = searchParams.get('category') ?? ''
  const actionRequired = searchParams.get('action_required') ?? ''
  const page = parseInt(searchParams.get('page') ?? '1', 10)

  const [searchInput, setSearchInput] = useState(search)
  const [showFilters, setShowFilters] = useState(false)

  const setParam = (key: string, value: string) => {
    const next = new URLSearchParams(searchParams)
    if (value) {
      next.set(key, value)
    } else {
      next.delete(key)
    }
    next.set('page', '1')
    setSearchParams(next)
  }

  const setPage = (p: number) => {
    const next = new URLSearchParams(searchParams)
    next.set('page', String(p))
    setSearchParams(next)
  }

  const clearFilters = () => {
    setSearchParams(new URLSearchParams())
    setSearchInput('')
  }

  const hasFilters = !!(search || priority || category || actionRequired)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await emailsApi.list({
        page,
        page_size: 20,
        search: search || undefined,
        priority: priority || undefined,
        category: category || undefined,
        action_required: actionRequired === 'true' ? true : undefined,
      })
      setEmails(data.items)
      setPagination({ total: data.total, page: data.page, totalPages: data.total_pages })
    } catch {
      setEmails([])
    } finally {
      setLoading(false)
    }
  }, [search, priority, category, actionRequired, page])

  useEffect(() => { load() }, [load])

  // Debounced search submit
  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') setParam('search', searchInput)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-800 bg-slate-900 sticky top-0 z-10">
        <div className="flex items-center gap-3 mb-3">
          <Inbox className="w-5 h-5 text-blue-400" />
          <h1 className="text-lg font-bold text-white">Inbox</h1>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-400">
            {pagination.total} emails
          </span>
        </div>

        {/* Search + filter row */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              placeholder="Search subject, sender, body... (press Enter)"
              className="input pl-9 text-sm"
            />
            {searchInput && (
              <button
                onClick={() => { setSearchInput(''); setParam('search', '') }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <button
            onClick={() => setShowFilters((v) => !v)}
            className={clsx(
              'btn-secondary flex items-center gap-1.5 flex-shrink-0',
              showFilters && 'bg-blue-600 text-white hover:bg-blue-500',
            )}
          >
            <SlidersHorizontal className="w-4 h-4" />
            Filters
            {hasFilters && (
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
            )}
          </button>
        </div>

        {/* Filter panel */}
        {showFilters && (
          <div className="mt-3 p-3 bg-slate-800 rounded-xl border border-slate-700 flex flex-wrap gap-3 items-end">
            <div>
              <p className="label">Priority</p>
              <select
                value={priority}
                onChange={(e) => setParam('priority', e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All</option>
                {PRIORITIES.filter(Boolean).map((p) => (
                  <option key={p} value={p} className="capitalize">{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                ))}
              </select>
            </div>

            <div>
              <p className="label">Category</p>
              <select
                value={category}
                onChange={(e) => setParam('category', e.target.value)}
                className="input text-sm py-1.5"
              >
                {CATEGORIES.map((c) => (
                  <option key={c} value={c}>{c || 'All Categories'}</option>
                ))}
              </select>
            </div>

            <div>
              <p className="label">Action Required</p>
              <select
                value={actionRequired}
                onChange={(e) => setParam('action_required', e.target.value)}
                className="input text-sm py-1.5"
              >
                <option value="">All</option>
                <option value="true">Yes</option>
              </select>
            </div>

            {hasFilters && (
              <button onClick={clearFilters} className="btn-ghost flex items-center gap-1 text-xs text-red-400 hover:text-red-300">
                <X className="w-3 h-3" /> Clear all
              </button>
            )}
          </div>
        )}
      </div>

      {/* Email list */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="space-y-0">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="px-5 py-4 border-b border-slate-800">
                <div className="flex gap-4">
                  <div className="w-2 h-2 rounded-full bg-slate-700 mt-2 animate-pulse" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 bg-slate-800 rounded w-1/3 animate-pulse" />
                    <div className="h-3 bg-slate-800 rounded w-1/2 animate-pulse" />
                    <div className="flex gap-2 mt-2">
                      <div className="h-5 w-16 bg-slate-800 rounded-full animate-pulse" />
                      <div className="h-5 w-24 bg-slate-800 rounded-full animate-pulse" />
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : emails.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 text-slate-500">
            <Inbox className="w-12 h-12 mb-3 opacity-30" />
            <p className="text-sm font-medium">No emails found</p>
            {hasFilters && (
              <button onClick={clearFilters} className="text-xs text-blue-400 mt-2 hover:text-blue-300">
                Clear filters
              </button>
            )}
          </div>
        ) : (
          emails.map((email) => <EmailCard key={email.id} email={email} />)
        )}
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="px-6 py-3 border-t border-slate-800 flex items-center justify-between">
          <p className="text-xs text-slate-500">
            Page {pagination.page} of {pagination.totalPages} · {pagination.total} total
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page <= 1}
              className="btn-ghost disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={page >= pagination.totalPages}
              className="btn-ghost disabled:opacity-30 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

import type React from 'react'
