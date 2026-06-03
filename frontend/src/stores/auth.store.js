import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { config } from '@/config'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null)
  const user = ref(null)
  const isInitialized = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || null)

  function setSession(token, userData) {
    accessToken.value = token
    user.value = userData
    
    if (userData?.username) {
      localStorage.setItem('agro_username', userData.username)
    }
  }

  function clearSession() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('agro_username')
  }

  async function checkPersistedSession() {
    try {
      const res = await axios.post(`${config.apiUrl}/api/v1/auth/refresh`, {}, { withCredentials: true })
      
      const token = res.data?.access_token || res.data?.data?.access_token
      
      if (!token) {
        throw new Error("Токен не найден в ответе рефреша")
      }

      const payload = JSON.parse(atob(token.split('.')[1]))

      const savedUsername = localStorage.getItem('agro_username') || 'admin'
      
      setSession(token, { 
        id: payload.sub, 
        username: savedUsername, 
        role: payload.role 
      })
    } catch (e) {
      clearSession()
      throw e
    }
  }

  return { accessToken, user, isInitialized, isAuthenticated, userRole, setSession, clearSession, checkPersistedSession }
})