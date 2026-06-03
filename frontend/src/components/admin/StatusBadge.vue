<template>
  <span 
    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[9px] font-black tracking-widest uppercase border select-none font-mono shadow-sm"
    :class="badgeClasses"
  >
    <span class="w-1.5 h-1.5 rounded-full" :class="dotClasses"></span>
    {{ label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true }
})

const badgeClasses = computed(() => {
  switch (props.status) {
    case 'NEW':
      return 'bg-blue-500/10 border-blue-500/30 text-blue-600 shadow-[0_2px_8px_rgba(59,130,246,0.1)]'
    case 'IN_PROGRESS':
      return 'bg-amber-500/10 border-amber-500/30 text-amber-600 shadow-[0_2px_8px_rgba(245,158,11,0.15)]'
    case 'DONE':
      return 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 shadow-[0_2px_8px_rgba(16,185,129,0.1)]'
    default:
      return 'bg-gray-500/10 border-gray-500/30 text-gray-600'
  }
})

const dotClasses = computed(() => {
  switch (props.status) {
    case 'NEW':
      return 'bg-blue-500 animate-pulse'
    case 'IN_PROGRESS':
      return 'bg-amber-500 animate-ping'
    case 'DONE':
      return 'bg-emerald-500'
    default:
      return 'bg-gray-500'
  }
})

const label = computed(() => {
  switch (props.status) {
    case 'NEW':
      return 'Новая'
    case 'IN_PROGRESS':
      return 'В работе'
    case 'DONE':
      return 'Завершена'
    default:
      return props.status
  }
})
</script>