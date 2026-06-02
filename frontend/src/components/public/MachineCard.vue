<template>
  <router-link :to="detailUrl" class="group flex flex-col bg-surface border border-border/60 rounded-2xl overflow-hidden hover:shadow-[0_15px_40px_rgba(0,0,0,0.05)] hover:-translate-y-1 transition-all duration-300">
    
    <div class="relative w-full aspect-[4/3] bg-bg overflow-hidden flex items-center justify-center">
      <img 
        v-if="machine.image_urls && machine.image_urls.length > 0" 
        :src="machine.image_urls[0]" 
        :alt="machine.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
      >
      <div v-else class="text-border/50 text-6xl">
        <svg class="w-16 h-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    </div>

    <div class="p-6 flex flex-col flex-grow">
      <h3 class="font-extrabold text-text-main text-lg uppercase tracking-wider mb-2 group-hover:text-primary transition-colors line-clamp-2">
        {{ machine.title }}
      </h3>
      
      <div class="mt-auto pt-4 flex justify-between items-end border-t border-border/50">
        <div>
          <span class="block text-[10px] text-text-muted font-bold tracking-widest uppercase mb-1">Стоимость</span>
          <span v-if="machine.price" class="text-xl font-extrabold text-accent font-mono">{{ formatPrice(machine.price) }}</span>
          <span v-else class="text-sm font-bold text-text-muted">По запросу</span>
        </div>
        
        <span class="text-primary text-xl translate-x-2 opacity-0 group-hover:translate-x-0 group-hover:opacity-100 transition-all">
          →
        </span>
      </div>
    </div>
    
  </router-link>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  machine: { type: Object, required: true }
})

const detailUrl = computed(() => {
  const slug = props.machine.title.toLowerCase().replace(/[^a-zа-я0-9]+/g, '-').replace(/(^-|-$)+/g, '')
  return `/machines/${props.machine.id}-${slug}`
})

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU', { style: 'currency', currency: 'RUB', maximumFractionDigits: 0 }).format(price)
}
</script>