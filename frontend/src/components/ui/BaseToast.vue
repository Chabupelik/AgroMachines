<template>
  <div class="fixed bottom-5 right-5 z-[99999] flex flex-col gap-2 pointer-events-none">
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
        class="pointer-events-auto flex items-center gap-3 px-5 py-3.5 rounded-lg border shadow-lg font-mono text-xs uppercase tracking-wider"
        :class="[
          toast.type === 'success' 
            ? 'bg-success/5 border-success/20 text-success' 
            : 'bg-danger/5 border-danger/20 text-danger'
        ]"
      >
        <span>{{ toast.type === 'success' ? '✅' : '🚨' }}</span>
        <span>{{ toast.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUiStore } from '@/stores/ui.store'

const uiStore = useUiStore()
const toasts = computed(() => uiStore.toasts)
</script>