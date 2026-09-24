import apiClient from './client'

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user_id: string
  name: string
  email: string
}

export const authApi = {
  login: (payload: LoginPayload) =>
    apiClient.post<TokenResponse>('/auth/login', payload).then((r) => r.data),

  register: (payload: RegisterPayload) =>
    apiClient.post<TokenResponse>('/auth/register', payload).then((r) => r.data),
}
