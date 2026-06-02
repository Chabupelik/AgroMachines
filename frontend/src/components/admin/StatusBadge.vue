<template>
  <span class="px-2.5 py-1 rounded-full border text-[10px] font-bold uppercase tracking-wider inline-block" :class="statusConfig.colorClass">
    {{ statusConfig.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'
import { LEAD_STATUSES } from '@/constants/lead-statuses'

const props = defineProps({
  status: { type: String, required: true }
})

const statusConfig = computed(() => {
  return LEAD_STATUSES[props.status] || { label: props.status, colorClass: 'border-border text-text-muted bg-black/10' }
})
</script>