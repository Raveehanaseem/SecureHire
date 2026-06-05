import { create } from 'zustand'
import api from '../utils/api'

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const { data } = await api.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })

      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      const user = { id: data.user_id, role: data.role, full_name: data.full_name }
      localStorage.setItem('user', JSON.stringify(user))

      set({ user, isAuthenticated: true, isLoading: false })
      return { success: true, role: data.role }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Login failed'
      set({ error: msg, isLoading: false })
      return { success: false, error: msg }
    }
  },

  register: async (payload) => {
    set({ isLoading: true, error: null })
    try {
      await api.post('/auth/register', payload)
      set({ isLoading: false })
      return { success: true }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed'
      set({ error: msg, isLoading: false })
      return { success: false, error: msg }
    }
  },

  logout: async () => {
    try { await api.post('/auth/logout') } catch {}
    localStorage.clear()
    set({ user: null, isAuthenticated: false })
  },

  clearError: () => set({ error: null }),
}))

export default useAuthStore
