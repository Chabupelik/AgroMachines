<template>
  <div class="fixed bottom-5 right-5 z-[99999] flex flex-col gap-3 pointer-events-none max-w-sm w-full px-4 sm:px-0">
    <transition-group
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform translate-y-4 opacity-0"
      enter-to-class="transform translate-y-0 opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform translate-y-0 opacity-100"
      leave-to-class="transform translate-y-4 opacity-0"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-start gap-4 p-4 rounded-xl border border-border bg-surface shadow-[0_10px_30px_rgba(0,0,0,0.08)] border-l-4"
        :class="[
          toast.type === 'success' ? 'border-l-success' : 'border-l-danger'
        ]"
      >
        <span class="text-lg shrink-0 select-none">
          {{ toast.type === 'success' ? '✅' : '🚨' }}
        </span>
        
        <div class="flex-grow space-y-1">
          <span class="block text-[10px] font-extrabold uppercase tracking-widest" :class="[toast.type === 'success' ? 'text-success' : 'text-danger']">
            {{ toast.type === 'success' ? 'Успешно' : 'Ошибка безопасности' }}
          </span>
          <p class="text-xs sm:text-sm text-text-main font-medium leading-relaxed normal-case">
            {{ toast.message }}
          </p>
        </div>
        
        <button @click="removeToast(toast.id)" class="text-text-muted hover:text-text-main transition-colors cursor-pointer text-xs select-none p-0.5">
          ✕
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui.store'

const uiStore = useUiStore()
const toasts = computed(() => uiStore.toasts)

function removeToast(id) {
  uiStore.toasts = uiStore.toasts.filter(t => t.id !== id)
}
</script>