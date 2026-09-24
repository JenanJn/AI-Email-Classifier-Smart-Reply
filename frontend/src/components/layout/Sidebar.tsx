import { NavLink, useNavigate } from 'react-router-dom'
import {
  Brain,
  LayoutDashboard,
  Inbox,
  BarChart3,
  PlusCircle,
  LogOut,
  Zap,
} from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'
import clsx from 'clsx'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Command Center', end: true },
  { to: '/inbox', icon: Inbox, label: 'Inbox' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/add', icon: PlusCircle, label: 'Add Email' },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="app-sidebar w-64 bg-[#111d25]/95 border-r border-[#8ea3a9]/10 flex flex-col flex-shrink-0 transition-all duration-200">
      {/* Logo */}
      <div className="sidebar-brand px-5 py-6 border-b border-[#8ea3a9]/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-[#e0ad5d] flex items-center justify-center flex-shrink-0 shadow-lg shadow-[#e0ad5d]/10">
            <Brain className="w-5 h-5 text-[#18232a]" />
          </div>
          <div className="sidebar-copy">
            <p className="text-sm font-bold text-white leading-tight">AI Email</p>
            <p className="text-xs text-[#e0ad5d] font-medium leading-tight">Command Center</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map(({ to, icon: Icon, label, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              clsx(
                'sidebar-nav-link flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-[#e0ad5d] text-[#18232a] shadow-lg shadow-[#e0ad5d]/10'
                  : 'text-[#9caeb0] hover:text-[#f5f2ea] hover:bg-[#293a43]',
              )
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="sidebar-user p-3 border-t border-[#8ea3a9]/10">
        <div className="flex items-center gap-3 px-2 py-2 rounded-lg">
          <div className="w-9 h-9 rounded-full bg-[#293a43] border border-[#e0ad5d]/40 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-white">
              {user?.name?.charAt(0).toUpperCase() ?? 'U'}
            </span>
          </div>
          <div className="sidebar-user-copy flex-1 min-w-0">
            <p className="text-xs font-semibold text-white truncate">{user?.name}</p>
            <p className="text-xs text-[#829397] truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 text-[#829397] hover:text-[#e07a5f] transition-colors rounded"
            title="Log out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
