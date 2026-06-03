import { useAuthStore } from '@/stores/auth.store'
import { ROUTE_NAMES } from '@/constants/routes'

export function roleGuard(to, from) {
  const authStore = useAuthStore()

  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    return { name: ROUTE_NAMES.FORBIDDEN }
  }
  return true
}