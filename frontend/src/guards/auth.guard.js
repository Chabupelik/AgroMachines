import { useAuthStore } from '@/stores/auth.store'
import { ROUTE_NAMES } from '@/constants/routes'

export async function authGuard(to) {
  const authStore = useAuthStore()

  if (!authStore.isInitialized) {
    try {
      await authStore.checkPersistedSession()
    } catch (e) {
    } finally {
      authStore.isInitialized = true
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return { name: ROUTE_NAMES.LOGIN }
  }
}