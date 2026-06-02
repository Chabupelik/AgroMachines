import { useAuthStore } from '@/stores/auth.store'
import { ROUTE_NAMES } from '@/constants/routes'

export function authGuard(to, from, next) {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.isAuthenticated) {
        return { name: ROUTE_NAMES.LOGIN }
    }
    next()
}