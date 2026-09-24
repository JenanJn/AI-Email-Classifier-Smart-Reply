import { useState, useCallback } from 'react'
import { authApi } from '../api/auth'
import type { User } from '../types'

export function useAuth() {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem('auth_user')
    return stored ? JSON.parse(stored) : null
  })
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('auth_token'),
  )

  const login = useCallback(async (email: string, password: string) => {
    const data = await authApi.login({ email, password })
    const userObj: User = { id: data.user_id, name: data.name, email: data.email }
    localStorage.setItem('auth_token', data.access_token)
    localStorage.setItem('auth_user', JSON.stringify(userObj))
    setToken(data.access_token)
    setUser(userObj)
    return userObj
  }, [])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const data = await authApi.register({ name, email, password })
    const userObj: User = { id: data.user_id, name: data.name, email: data.email }
    localStorage.setItem('auth_token', data.access_token)
    localStorage.setItem('auth_user', JSON.stringify(userObj))
    setToken(data.access_token)
    setUser(userObj)
    return userObj
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
    setToken(null)
    setUser(null)
  }, [])

  return { user, token, login, register, logout, isAuthenticated: !!token }
}
