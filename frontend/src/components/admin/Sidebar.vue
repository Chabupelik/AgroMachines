<template>
  <div>
    <transition enter-active-class="transition-opacity duration-300" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="isOpen" class="md:hidden fixed inset-0 z-[999] bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
    </transition>
    
    <aside
      class="fixed top-0 left-0 h-full w-[240px] bg-[#111613] border-r border-[#1e2520] z-[1000] flex flex-col transition-transform duration-300 md:translate-x-0 text-[#8ba2b5]"
      :class="[isOpen ? 'translate-x-0' : '-translate-x-full']"
    >
      <div class="p-6 h-[64px] border-b border-[#1e2520] flex justify-between items-center select-none shrink-0">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="18" r="2" />
            <path d="M6 16h12" />
            <path d="M8 16V10h6v6" />
            <path d="M14 10l2 3h2v3" />
            <path d="M10 10V8h1" />
          </svg>
          <span class="font-black text-[#f0f4f8] tracking-[2px] uppercase text-sm">AgroPanel</span>
        </div>
        <button @click="$emit('close')" class="md:hidden text-[#8ba2b5] hover:text-[#f0f4f8] transition-colors cursor-pointer focus:outline-none">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
      
      <nav class="flex-grow p-4 space-y-1.5 text-xs uppercase tracking-wider font-bold">
        <router-link to="/admin/leads" @click="$emit('close')" class="nav-item">
          <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
          Заявки
        </router-link>
        
        <router-link to="/admin/machines" @click="$emit('close')" class="nav-item">
          <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          Техника
        </router-link>
        
        <router-link to="/admin/users" @click="$emit('close')" class="nav-item">
          <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          Персонал
        </router-link>
        
        <router-link to="/admin/audit" @click="$emit('close')" class="nav-item">
          <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
          Логи аудита
        </router-link>
      </nav>

      <div class="p-4 border-t border-[#1e2520]">
        <button 
          @click="handleLogout"
          class="w-full flex items-center justify-center gap-2.5 px-4 py-3 rounded-lg border border-danger/20 bg-danger/5 text-danger hover:bg-danger/10 text-xs font-bold uppercase tracking-wider transition-all duration-200 cursor-pointer"
        >
          <svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
            <polyline points="16 17 21 12 16 7"></polyline>
            <line x1="21" y1="12" x2="9" y2="12"></line>
          </svg>
          Выйти
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

defineProps({
  isOpen: { type: Boolean, required: true }
})
const emit = defineEmits(['close'])

const router = useRouter()
const { logout } = useAuth()

async function handleLogout() {
  emit('close')
  await logout()
  router.push('/login')
}
</script>

<style scoped>
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #8ba2b5;
  transition: all 0.2s ease-in-out;
}

.nav-item:hover {
  background: rgba(196, 164, 117, 0.05);
  color: var(--color-accent);
}

.router-link-active {
  background: rgba(196, 164, 117, 0.1) !important;
  color: var(--color-accent) !important;
  border-left: 3px solid var(--color-accent);
  border-radius: 0 8px 8px 0;
}
</style>