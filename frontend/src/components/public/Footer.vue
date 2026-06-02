<template>
  <footer class="bg-surface border-t border-border/50 py-12 px-6 text-sm text-text-muted">
    <div class="max-w-[1600px] mx-auto grid grid-cols-1 md:grid-cols-3 gap-10 items-start">
      
      <div class="space-y-4">
        <router-link to="/" class="flex items-center gap-3 cursor-pointer select-none">
          <svg class="w-6 h-6 text-accent" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="18" cy="18" r="3" /><circle cx="6" cy="18" r="2" />
            <path d="M6 16h12M8 16V10h6v6M14 10l2 3h2v3M10 10V8h1" />
          </svg>
          <span class="font-extrabold text-text-main tracking-[2px] uppercase text-sm">{{ config.siteName }}</span>
        </router-link>
        <div class="text-text-muted text-xs leading-relaxed">
          © {{ currentYear }} {{ config.companyName }}.<br>
          Все права защищены.
        </div>
      </div>

      <div class="space-y-3 text-xs sm:text-sm">
        <span class="text-text-main font-bold block text-sm">Реквизиты компании</span>
        <div>Адрес: <span class="text-text-main">{{ config.companyAddress }}</span></div>
        <div>ИНН: <span class="text-text-main font-mono">{{ config.companyInn }}</span></div>
        <div>ОГРН: <span class="text-text-main font-mono">{{ config.companyOgrn }}</span></div>
      </div>
      
      <div class="space-y-6 md:text-right text-xs sm:text-sm">
        <div class="space-y-1.5">
          <span class="text-text-main font-bold block text-sm">Обратная связь</span>
          <div>Телефон: <a :href="`tel:${config.supportPhone}`" class="text-primary hover:underline font-mono">{{ config.supportPhone }}</a></div>
          <div>Email: <a :href="`mailto:${config.supportEmail}`" class="text-primary hover:underline font-mono">{{ config.supportEmail }}</a></div>
        </div>
        
        <div class="flex flex-col md:items-end gap-2 border-t border-border/50 pt-4 text-xs font-medium">
          <router-link to="/policy" class="hover:text-primary transition-colors">Политика конфиденциальности</router-link>
          <router-link to="/terms" class="hover:text-primary transition-colors">Согласие на обработку ПДН</router-link>
        </div>
      </div>

    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { config } from '@/config'
const currentYear = computed(() => new Date().getFullYear())
</script>