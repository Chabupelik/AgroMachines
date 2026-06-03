import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useUiStore } from '@/stores/ui.store'
import { authApi } from '@/services/auth.api'
import { mapApiError } from '@/utils/apiErrors'

export function useAuth() {
  const authStore = useAuthStore()
  const uiStore = useUiStore()

  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const userRole = computed(() => authStore.userRole)
  const currentUser = computed(() => authStore.user)

  async function login(username, password) {
    try {
      const res = await authApi.login(username, password)
      console.log(res)
      const token = res.access_token
      const role = res.role
      
      const payload = JSON.parse(atob(token.split('.')[1]))
      
      authStore.setSession(token, { id: payload.sub, username, role })
      uiStore.addToast("Успешный вход в систему", "success")
      return true
    } catch (err) {
      const message = mapApiError(err)
      uiStore.addToast(message, "error")
      return false
    }
  }

  async function logout() {
    try {
      await authApi.logout()
    } catch (err) {
    } finally {
      authStore.clearSession()
      uiStore.addToast("Сессия завершена", "success")
    }
  }

  return { isAuthenticated, userRole, currentUser, login, logout }
}