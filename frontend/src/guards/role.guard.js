import { useAuthStore } from '@/stores/auth.store'
import { ROUTE_NAMES } from '@/constants/routes'

export function roleGuard(to, from, next) {
  const authStore = useAuthStore()

  if (to.meta.roles && !to.meta.roles.includes(authStore.userRole)) {
    return next({ name: ROUTE_NAMES.FORBIDDEN })
  }
  next()
}