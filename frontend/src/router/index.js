import { createRouter, createWebHistory } from 'vue-router'
import { ROUTE_NAMES } from '@/constants/routes'
import { ROLES } from '@/constants/roles'
import { authGuard } from '@/guards/auth.guard'
import { roleGuard } from '@/guards/role.guard'

import HomeView from '@/views/public/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: ROUTE_NAMES.HOME,
      component: HomeView
    },
    {
      path: '/machines',
      name: ROUTE_NAMES.CATALOG,
      component: () => import('@/views/public/MachineCatalog.vue')
    },
    {
      path: '/machines/:id-:slug',
      name: ROUTE_NAMES.DETAIL,
      component: () => import('@/views/public/MachineDetail.vue')
    },
    {
      path: '/policy',
      name: ROUTE_NAMES.POLICY,
      component: () => import('@/views/public/DocumentView.vue'),
      meta: { document: 'policy' }
    },
    {
      path: '/terms',
      name: ROUTE_NAMES.TERMS,
      component: () => import('@/views/public/DocumentView.vue'),
      meta: { document: 'terms' }
    },
    
    {
      path: '/login',
      name: ROUTE_NAMES.LOGIN,
      component: () => import('@/views/admin/LoginView.vue')
    },

    {
      path: '/admin/leads',
      name: ROUTE_NAMES.ADMIN_LEADS,
      component: () => import('@/views/admin/LeadsView.vue'),
      meta: { requiresAuth: true, roles: [ROLES.SUPERADMIN, ROLES.MANAGER] }
    },
    {
      path: '/admin/machines',
      name: ROUTE_NAMES.ADMIN_MACHINES,
      component: () => import('@/views/admin/MachinesView.vue'),
      meta: { requiresAuth: true, roles: [ROLES.SUPERADMIN, ROLES.EDITOR] }
    },
    {
      path: '/admin/users',
      name: ROUTE_NAMES.ADMIN_USERS,
      component: () => import('@/views/admin/UsersView.vue'),
      meta: { requiresAuth: true, roles: [ROLES.SUPERADMIN] }
    },
    {
      path: '/admin/audit',
      name: ROUTE_NAMES.ADMIN_AUDIT,
      component: () => import('@/views/admin/AuditView.vue'),
      meta: { requiresAuth: true, roles: [ROLES.SUPERADMIN] }
    },

    {
      path: '/403',
      name: ROUTE_NAMES.FORBIDDEN,
      component: () => import('@/views/admin/ForbiddenView.vue')
    },
    {
      path: '/:pathMatch(.*)*',
      name: ROUTE_NAMES.NOT_FOUND,
      component: () => import('@/views/public/NotFoundView.vue')
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (to.hash) {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            el: to.hash,
            behavior: 'smooth'
          })
        }, 250)
      })
    }
    return { top: 0, behavior: 'smooth' }
  }
})


router.beforeEach(authGuard)
router.beforeEach(roleGuard)

export default router