<template>
  <div class="animate-pulse bg-surface border border-border/50 rounded-lg w-full" :class="heightClass"></div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  height: { type: String, default: 'md' } // 'sm' | 'md' | 'lg' | 'xl'
})

const heightClass = computed(() => {
  const heights = {
    sm: 'h-4',
    md: 'h-12',
    lg: 'h-48',
    xl: 'h-64'
  }
  return heights[props.height] || heights.md
})
</script>