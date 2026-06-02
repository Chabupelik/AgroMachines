import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/public/HomeView.vue'
import LeadsView from '@/views/admin/LeadsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/admin/leads',
      name: 'admin-leads',
      component: LeadsView
    }
  ]
})

export default router