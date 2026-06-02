<template>
  <div v-if="total > limit" class="flex justify-center items-center gap-2 mt-8 font-mono text-xs select-none">
    <button
      :disabled="offset === 0"
      @click="$emit('change', offset - limit)"
      class="px-4 py-2 rounded-lg border border-border bg-surface text-text-muted hover:text-text-main hover:border-text-muted disabled:opacity-30 disabled:pointer-events-none cursor-pointer transition-colors"
    >
      ◀ назад
    </button>
    
    <span class="text-text-muted px-2">
      стр. <b class="text-accent">{{ currentPage }}</b> из <b class="text-text-main">{{ totalPages }}</b>
    </span>

    <button
      :disabled="offset + limit >= total"
      @click="$emit('change', offset + limit)"
      class="px-4 py-2 rounded-lg border border-border bg-surface text-text-muted hover:text-text-main hover:border-text-muted disabled:opacity-30 disabled:pointer-events-none cursor-pointer transition-colors"
    >
      вперед ▶
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  total: { type: Number, required: true },
  limit: { type: Number, required: true },
  offset: { type: Number, required: true }
})

defineEmits(['change'])

const currentPage = computed(() => Math.floor(props.offset / props.limit) + 1)
const totalPages = computed(() => Math.ceil(props.total / props.limit) || 1)
</script>