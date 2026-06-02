<template>
  <div class="animate-pulse bg-gray-200 rounded-lg w-full" :class="heightClass"></div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  height: { type: String, default: 'md' }
})
const heightClass = computed(() => {
  const heights = {
    sm: 'h-4',
    md: 'h-10',
    lg: 'h-48',
    xl: 'h-64'
  }
  return heights[props.height] || heights.md
})
</script>