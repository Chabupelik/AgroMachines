<template>
  <router-link 
    :to="`/machines/${machine.id}-${slugify(machine.title)}`"
    class="group relative bg-surface border border-border/50 rounded-[24px] p-4 flex flex-col gap-4 hover:shadow-xl transition-all duration-300 no-underline max-w-[420px] mx-auto w-full"
  >
    <div class="relative overflow-hidden rounded-[18px] aspect-[4/3] bg-bg flex items-center justify-center shrink-0">
      
      <img 
        v-if="machine.image_urls?.length" 
        :src="machine.image_urls[0]" 
        class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105" 
        :alt="machine.title"
      />
      <div v-else class="text-border/40">
        <svg class="w-12 h-12 stroke-current" viewBox="0 0 24 24" fill="none" stroke-width="1.5">
          <circle cx="18" cy="18" r="3" />
          <circle cx="6" cy="18" r="2" />
          <path d="M6 16h12" />
          <path d="M8 16V10h6v6" />
          <path d="M14 10l2 3h2v3" />
          <path d="M10 10V8h1" />
        </svg>
      </div>

      <span 
        class="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-widest border shadow-sm z-10 select-none font-mono"
        :class="[
          machine.is_available 
            ? 'bg-surface border-primary/30 text-primary' 
            : 'bg-surface border-orange-500/30 text-orange-600'
        ]"
      >
        {{ machine.is_available ? 'В наличии' : 'Под заказ' }}
      </span>
    </div>

    <div class="flex-grow flex flex-col justify-between text-left">
      <div class="space-y-1">
        <h3 class="text-sm font-bold text-primary uppercase tracking-wider truncate group-hover:text-accent transition-colors duration-200">
          {{ machine.title }}
        </h3>
        <p class="text-xs text-text-muted line-clamp-2 leading-relaxed">
          {{ machine.description || 'Описание временно отсутствует.' }}
        </p>
      </div>
      
      <div class="pt-3 border-t border-border/20 flex justify-between items-center mt-3 shrink-0">
        <span v-if="machine.price" class="text-sm font-black text-accent font-mono">
          {{ formatPrice(machine.price) }}
        </span>
        <span v-else class="text-[10px] font-bold text-text-muted uppercase tracking-wider font-mono">
          По запросу
        </span>

        <div class="text-text-muted group-hover:text-accent transition-colors duration-200">
          <svg class="w-4 h-4 transform group-hover:translate-x-0.5 transition-transform duration-200" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="5" y1="12" x2="19" y2="12"></line>
            <polyline points="12 5 19 12 12 19"></polyline>
          </svg>
        </div>
      </div>
    </div>
  </router-link>
</template>

<script setup>
defineProps({
  machine: { type: Object, required: true }
})

function formatPrice(val) {
  return new Intl.NumberFormat('ru-RU').format(val) + ' ₽'
}

function translite(str) {
  const ru = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 
    'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 
    'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 
    'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 
    'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 
    'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 
    'э': 'e', 'ю': 'yu', 'я': 'ya'
  }
  return str.split('').map(c => {
    const l = c.toLowerCase()
    return ru[l] !== undefined ? ru[l] : c
  }).join('')
}

function slugify(text) {
  const translited = translite(text.toString())
  
  const slug = translited
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
  return slug || 'model'
}
</script>