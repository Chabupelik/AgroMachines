<template>
  <div>
    <transition enter-active-class="transition-opacity duration-300" enter-from-class="opacity-0" enter-to-class="opacity-100" leave-active-class="transition-opacity duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
      <div v-if="isOpen" class="md:hidden fixed inset-0 z-[999] bg-black/40 backdrop-blur-sm" @click="$emit('close')"></div>
    </transition>
    <aside
      class="fixed top-0 left-0 h-full w-[240px] bg-[#111613] border-r border-[#1e2520] z-[1000] flex flex-col transition-transform duration-300 md:translate-x-0 text-[#8ba2b5]"
      :class="[isOpen ? 'translate-x-0' : '-translate-x-full']"
    >
      <div class="p-6 border-b border-[#1e2520] flex justify-between items-center select-none">
        <div class="flex items-center gap-3">
          <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="18" cy="18" r="3" />
            <circle cx="6" cy="18" r="2" />
            <path d="M6 16h12" />
            <path d="M8 16V10h6v6" />
            <path d="M14 10l2 3h2v3" />
            <path d="M10 10V8h1" />
          </svg>
          <span class="font-extrabold text-[#f0f4f8] tracking-[1px] uppercase text-sm">AgroPanel</span>
        </div>
        <button @click="$emit('close')" class="md:hidden text-[#8ba2b5] hover:text-[#f0f4f8] transition-colors cursor-pointer text-sm">
          ✕
        </button>
      </div>
      
      <nav class="flex-grow p-4 space-y-1 text-sm">
        <router-link to="/admin/leads" @click="$emit('close')" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-primary/20 hover:text-accent transition-all duration-200">
          <span>📋</span> Заявки
        </router-link>
        <router-link to="/admin/machines" @click="$emit('close')" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-primary/20 hover:text-accent transition-all duration-200">
          <span>⚙️</span> Техника
        </router-link>
        <router-link to="/admin/users" @click="$emit('close')" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-primary/10 hover:text-accent transition-all duration-200">
          <span>👥</span> Персонал
        </router-link>
        <router-link to="/admin/audit" @click="$emit('close')" class="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-primary/10 hover:text-accent transition-all duration-200">
          <span>🪵</span> Логи аудита
        </router-link>
      </nav>

      <div class="p-4 border-t border-[#1e2520]">
        <button class="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-danger/20 bg-danger/5 text-danger hover:bg-danger/10 text-xs font-bold uppercase tracking-wider transition-all duration-200 cursor-pointer">
          <span>🚪</span> Выйти
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
defineProps({
  isOpen: { type: Boolean, required: true }
})
defineEmits(['close'])
</script>

<style scoped>
.router-link-active {
  background: rgba(196, 164, 117, 0.15) !important;
  color: var(--color-accent) !important;
  border-left: 3px solid var(--color-accent);
  border-radius: 0 8px 8px 0;
}
</style>