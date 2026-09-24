import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { PlusCircle, Sparkles, ChevronDown, ChevronUp, CheckCircle } from 'lucide-react'
import { emailsApi } from '../api/emails'

// ── Sample emails for quick demo ──────────────────────────────────────────────
const SAMPLE_EMAILS = [
  {
    label: 'Interview Invitation',
    category: 'Job / Career',
    data: {
      sender_name: 'HR Team — TechCorp',
      sender_email: 'hr@techcorp.com',
      subject: 'Interview Invitation — Software Engineer Role',
      body: `Dear Candidate,

We are pleased to invite you for an interview for the Software Engineer position at TechCorp.

Your interview is scheduled for tomorrow at 10:00 AM at our Bangalore office (4th Floor, Tech Park, MG Road).

Please confirm your availability by replying to this email. Bring a copy of your resume and a government-issued ID.

We look forward to meeting you.

Best regards,
Priya Sharma
HR Manager, TechCorp`,
    },
  },
  {
    label: 'Bank Security Alert',
    category: 'Finance / Banking',
    data: {
      sender_name: 'HDFC Bank Security',
      sender_email: 'alerts@hdfcbank.com',
      subject: 'URGENT: Suspicious Activity on Your Account',
      body: `Dear Customer,

We have detected suspicious login activity on your HDFC Bank account from an unrecognized device.

For your security, please verify your identity immediately by logging into your account.

If this was NOT you, call our 24x7 helpline immediately: 1800-XXX-XXXX

Do not share your OTP or password with anyone.

Regards,
HDFC Bank Security Team`,
    },
  },
  {
    label: 'Assignment Deadline',
    category: 'Education',
    data: {
      sender_name: 'Prof. Rajesh Kumar',
      sender_email: 'r.kumar@university.edu',
      subject: 'Assignment Due This Friday — DBMS Unit 4',
      body: `Dear Students,

This is a reminder that the assignment for Database Management Systems (Unit 4 — Normalization) is due this Friday at 11:59 PM.

Please submit your work through the student portal. Late submissions will not be accepted.

Topics to cover:
1. First Normal Form (1NF)
2. Second Normal Form (2NF)
3. Third Normal Form (3NF)

Contact me before Thursday if you have questions.

Regards,
Prof. Rajesh Kumar`,
    },
  },
  {
    label: 'Order Shipped',
    category: 'E-commerce',
    data: {
      sender_name: 'Amazon Order Updates',
      sender_email: 'order-update@amazon.in',
      subject: 'Your Order #AMZ-847291 Has Been Shipped',
      body: `Hello,

Great news! Your order has been shipped and is on its way.

Order Details:
- Order ID: #AMZ-847291
- Item: Sony WH-1000XM5 Wireless Headphones
- Tracking: AMZN-TRK-29847321
- Estimated Delivery: 2 business days

Thank you for shopping with Amazon!`,
    },
  },
  {
    label: 'Doctor Appointment',
    category: 'Healthcare',
    data: {
      sender_name: 'City Hospital',
      sender_email: 'appointments@cityhospital.com',
      subject: 'Appointment Confirmed — Dr. Priya Nair, Tomorrow at 11 AM',
      body: `Dear Patient,

Your appointment has been confirmed.

Doctor: Dr. Priya Nair (Cardiologist)
Date: Tomorrow
Time: 11:00 AM
Location: City Hospital, Room 204

Please arrive 10 minutes early and bring:
- Previous medical reports
- List of current medications
- Government-issued photo ID

City Hospital`,
    },
  },
  {
    label: 'Flight Booking',
    category: 'Travel',
    data: {
      sender_name: 'IndiGo Airlines',
      sender_email: 'noreply@goindigo.in',
      subject: 'Booking Confirmed — 6E-847 Mumbai to Delhi',
      body: `Dear Passenger,

Your flight booking is confirmed.

Flight: IndiGo 6E-847
Route: Mumbai (BOM) → Delhi (DEL)
Date: November 15, 2026
Departure: 07:30 AM | Arrival: 09:45 AM
PNR: INDG847291 | Seat: 14C

Online check-in opens 48 hours before departure.

Have a pleasant journey!
IndiGo Customer Team`,
    },
  },
  {
    label: 'Promotional Sale',
    category: 'Promotions',
    data: {
      sender_name: 'Amazon Deals',
      sender_email: 'deals@amazon.in',
      subject: 'FLASH SALE: Up to 70% Off — Ends Tonight!',
      body: `Don't miss our biggest sale of the year!

FLASH SALE — Ending Tonight at Midnight

- 70% off on Electronics
- 60% off on Fashion
- 50% off on Home & Kitchen

Top deals:
- Apple AirPods Pro: ₹15,999 (Was ₹26,999)
- Kindle Paperwhite: ₹7,999 (Was ₹13,999)

Shop now before deals expire!`,
    },
  },
  {
    label: 'Job Offer Letter',
    category: 'Job / Career',
    data: {
      sender_name: 'GlobalTech HR',
      sender_email: 'hr@globaltech.io',
      subject: 'Offer Letter — Senior Software Engineer Position',
      body: `Dear Candidate,

We are delighted to extend this formal offer of employment to you.

Position: Senior Software Engineer
Department: Platform Engineering
Location: Hyderabad (Hybrid)
Starting Date: December 1, 2026

Annual CTC: ₹18,00,000
Please sign and return the attached offer letter by November 28, 2026.

Best regards,
Anjali Mehta, Head of HR
GlobalTech`,
    },
  },
]

export default function AddEmail() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'manual' | 'sample'>('manual')
  const [expandedSample, setExpandedSample] = useState<number | null>(null)

  // Form state
  const [senderName, setSenderName] = useState('')
  const [senderEmail, setSenderEmail] = useState('')
  const [subject, setSubject] = useState('')
  const [body, setBody] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fillSample = (idx: number) => {
    const s = SAMPLE_EMAILS[idx]
    setSenderName(s.data.sender_name)
    setSenderEmail(s.data.sender_email)
    setSubject(s.data.subject)
    setBody(s.data.body)
    setMode('manual')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!body.trim()) { setError('Email body is required.'); return }
    setLoading(true)
    setError(null)
    try {
      const email = await emailsApi.create({
        sender_name: senderName || undefined,
        sender_email: senderEmail || undefined,
        subject: subject || undefined,
        body,
      })
      navigate(`/inbox/${email.id}`)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      const message = !err?.response
        ? 'The API is unavailable. Start the backend and try again.'
        : err.response.status >= 500
        ? 'The server could not analyze this email. Please try again.'
        : null
      setError(
        Array.isArray(detail)
          ? detail.map((d: any) => d.msg).join(', ')
          : detail ?? message ?? 'Failed to add email. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const clearForm = () => {
    setSenderName(''); setSenderEmail(''); setSubject(''); setBody(''); setError(null)
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <PlusCircle className="w-6 h-6 text-blue-400" />
          Add Email
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Enter an email to classify, prioritize, and generate a smart reply.
        </p>
      </div>

      {/* Mode tabs */}
      <div className="flex rounded-lg bg-slate-800 p-1 mb-6 w-fit">
        {(['manual', 'sample'] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all capitalize ${
              mode === m ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            {m === 'manual' ? 'Enter Manually' : 'Choose Sample'}
          </button>
        ))}
      </div>

      {/* Sample picker */}
      {mode === 'sample' && (
        <div className="space-y-2 mb-6 animate-fade-in">
          <p className="text-xs text-slate-500 mb-3">
            Click a sample to preview it, then click "Use this sample" to fill the form.
          </p>
          {SAMPLE_EMAILS.map((s, i) => (
            <div key={i} className="card border border-slate-700">
              <button
                onClick={() => setExpandedSample(expandedSample === i ? null : i)}
                className="w-full flex items-center justify-between text-left"
              >
                <div className="flex items-center gap-3">
                  <Sparkles className="w-4 h-4 text-blue-400 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-semibold text-white">{s.label}</p>
                    <p className="text-xs text-slate-500">{s.category} · {s.data.sender_name}</p>
                  </div>
                </div>
                {expandedSample === i ? (
                  <ChevronUp className="w-4 h-4 text-slate-400" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-slate-400" />
                )}
              </button>

              {expandedSample === i && (
                <div className="mt-3 pt-3 border-t border-slate-700 animate-fade-in">
                  <p className="text-xs text-slate-400 font-medium mb-1">Subject: {s.data.subject}</p>
                  <pre className="text-xs text-slate-500 whitespace-pre-wrap font-sans leading-relaxed line-clamp-6">
                    {s.data.body}
                  </pre>
                  <button
                    onClick={() => fillSample(i)}
                    className="btn-primary text-xs mt-3 flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    Use this sample
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Manual form */}
      {mode === 'manual' && (
        <form onSubmit={handleSubmit} className="card space-y-4 animate-fade-in">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="label">Sender Name</label>
              <input
                type="text"
                value={senderName}
                onChange={(e) => setSenderName(e.target.value)}
                placeholder="e.g. HR Team"
                className="input"
              />
            </div>
            <div>
              <label className="label">Sender Email</label>
              <input
                type="email"
                value={senderEmail}
                onChange={(e) => setSenderEmail(e.target.value)}
                placeholder="e.g. hr@company.com"
                className="input"
              />
            </div>
          </div>

          <div>
            <label className="label">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Email subject line"
              className="input"
            />
          </div>

          <div>
            <label className="label">Email Body <span className="text-red-400">*</span></label>
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder="Paste or type the email content here..."
              rows={12}
              required
              className="input resize-none font-mono text-sm leading-relaxed"
            />
          </div>

          {error && (
            <div className="bg-red-500/15 border border-red-500/30 rounded-lg px-3 py-2 text-sm text-red-300">
              {error}
            </div>
          )}

          <div className="flex items-center gap-3 pt-2">
            <button
              type="submit"
              disabled={loading || !body.trim()}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Analyzing with AI...
                </span>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Analyze with AI
                </>
              )}
            </button>
            {(body || subject || senderName) && (
              <button type="button" onClick={clearForm} className="btn-ghost text-sm">
                Clear
              </button>
            )}
          </div>

          <p className="text-xs text-slate-500">
            The AI will classify the category, detect intent, score priority, extract entities, and generate a smart reply automatically.
          </p>
        </form>
      )}
    </div>
  )
}

import type React from 'react'
