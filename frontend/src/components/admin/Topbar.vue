<template>
  <header class="w-full h-[64px] bg-surface/90 backdrop-blur-md border-b border-border/40 px-6 flex justify-between items-center select-none shrink-0 shadow-sm">
    <div class="flex items-center gap-4">
      <button 
        @click="$emit('toggle-sidebar')" 
        class="md:hidden p-1.5 rounded-lg text-primary hover:bg-primary/5 transition-colors cursor-pointer"
        aria-label="Открыть меню"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>
      <h2 class="text-base sm:text-lg text-text-main hidden sm:block font-bold tracking-wide">
        Система управления Агропром
      </h2>
    </div>

    <div v-if="currentUser" class="flex items-center gap-3">
      <div class="text-right">
        <span class="text-sm text-text-main block font-extrabold leading-tight">
          {{ currentUser.username }}
        </span>
        <span class="text-[10px] text-accent font-bold tracking-wider uppercase leading-none font-mono">
          {{ currentUser.role }}
        </span>
      </div>
      <div class="w-9 h-9 rounded-xl bg-primary/5 border border-primary/10 flex items-center justify-center text-primary font-black text-xs shadow-inner">
        {{ userInitial }}
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

defineEmits(['toggle-sidebar'])

const { currentUser } = useAuth()

const userInitial = computed(() => {
  return (currentUser.value?.username?.[0] || 'A').toUpperCase()
})
</script>