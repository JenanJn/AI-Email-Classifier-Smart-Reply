import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import EmailInbox from './pages/EmailInbox'
import EmailDetail from './pages/EmailDetail'
import Analytics from './pages/Analytics'
import AddEmail from './pages/AddEmail'
import Login from './pages/Login'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="inbox" element={<EmailInbox />} />
          <Route path="inbox/:id" element={<EmailDetail />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="add" element={<AddEmail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

import type React from 'react'
