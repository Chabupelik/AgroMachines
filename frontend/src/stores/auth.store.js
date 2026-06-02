import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || null)

  function setSession(token, userData) {
    accessToken.value = token
    user.value = userData
  }

  function clearSession() {
    accessToken.value = null
    user.value = null
  }

  return { accessToken, user, isAuthenticated, userRole, setSession, clearSession }
})